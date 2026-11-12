"""Business-cycle data: download, construct, detrend, and summarize.

Data sources (no API key needed):
  * FRED (St. Louis Fed), via the public ``fredgraph.csv`` endpoint.
  * Fernald (SF Fed) quarterly TFP database: business-sector output, hours, capital.

Typical use::

    import bcdata
    raw    = bcdata.load_raw()                 # download (or fall back to snapshot)
    levels = bcdata.build_series(raw)          # per-capita levels, real rate, TFP
    cycles = bcdata.hp_cycles(levels)          # % deviations from HP trend
    table  = bcdata.bc_moments(cycles)         # the business-cycle-facts table
"""

from __future__ import annotations

import io
import ssl
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.filters.hp_filter import hpfilter

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
FERNALD_URL = "https://www.frbsf.org/wp-content/uploads/quarterly_tfp.xlsx"
SNAPSHOT = Path(__file__).resolve().parent.parent / "data" / "bcdata_snapshot.csv"

# FRED code -> short name.  "pc" = already per capita (chained 2017 $ per person).
FRED_SERIES = {
    "A796RX0Q048SBEA": "C_nondurables_pc",  # real PCE nondurables per capita
    "A797RX0Q048SBEA": "C_services_pc",     # real PCE services per capita
    "A795RX0Q048SBEA": "C_durables_pc",     # real PCE durables per capita
    "GPDIC1": "I_private",                  # real gross private domestic investment, bn $
    "COMPRNFB": "real_wage",                # real hourly compensation, nonfarm business (index)
    "TB3MS": "tbill",                       # 3-month T-bill rate, % p.a. (monthly)
    "GDPDEF": "gdp_deflator",               # GDP implicit price deflator (index)
    "PAYEMS": "employment",                 # nonfarm payroll employment, thousands (monthly)
    "B230RC0Q173SBEA": "population",        # population, thousands
    "USRECQ": "recession",                  # NBER recession indicator (quarterly)
}

# Fernald growth rates (annualized % log changes) that we cumulate into levels.
FERNALD_SERIES = {"dY": "Y_business", "dhours": "hours", "dk": "capital"}

# Capital share used for the Solow residual.
ALPHA = 0.35


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------
def _ssl_context():
    # Some Python installs (e.g. pyenv/python.org on macOS) lack root certificates;
    # use certifi's bundle when it is available.
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _get(url: str, timeout: int = 30, retries: int = 3) -> bytes:
    # Note: keep Python's default User-Agent; FRED stalls some custom/browser-like ones.
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=timeout, context=_ssl_context()) as r:
                return r.read()
        except Exception:
            if attempt == retries - 1:
                raise


def download_fred(codes=FRED_SERIES) -> pd.DataFrame:
    """Download FRED series and average them to quarterly frequency."""
    out = {}
    for code, name in codes.items():
        df = pd.read_csv(io.BytesIO(_get(FRED_URL.format(code))),
                         index_col=0, parse_dates=True, na_values=".")
        out[name] = df.iloc[:, 0].astype(float).resample("QS").mean()
    return pd.DataFrame(out)


def download_fernald() -> pd.DataFrame:
    """Download Fernald's quarterly TFP file and turn growth rates into log levels.

    The file reports annualized quarterly growth rates in percent (100 x 4 x dlog).
    We cumulate dlog = rate/400 starting from log level 0 in 1947Q1.
    """
    q = pd.read_excel(io.BytesIO(_get(FERNALD_URL)), sheet_name="quarterly", header=1)
    q = q[q["date"].astype(str).str.fullmatch(r"\d{4}:Q[1-4]")].copy()
    q.index = pd.PeriodIndex(q["date"].str.replace(":", ""), freq="Q").to_timestamp()
    out = {}
    for col, name in FERNALD_SERIES.items():
        g = pd.to_numeric(q[col], errors="coerce").fillna(0.0) / 400.0
        out["log_" + name] = g.cumsum()
    return pd.DataFrame(out)


def load_raw(start="1947-01-01", end=None, use_snapshot: bool | None = None,
             save_snapshot: bool = True) -> pd.DataFrame:
    """Return raw quarterly data.

    use_snapshot=None (default): try to download; fall back to the saved snapshot.
    use_snapshot=True: read only the snapshot (fully reproducible, works offline).
    use_snapshot=False: download, raise on failure.
    """
    raw = None
    if use_snapshot is not True:
        try:
            raw = download_fred().join(download_fernald(), how="inner")
            if save_snapshot:
                SNAPSHOT.parent.mkdir(exist_ok=True)
                raw.to_csv(SNAPSHOT)
            print(f"Downloaded data: {raw.index[0].date()} to {raw.dropna().index[-1].date()}")
        except Exception as e:  # network problem, site change, ...
            if use_snapshot is False:
                raise
            print(f"Download failed ({e!r}); using snapshot {SNAPSHOT.name}")
    if raw is None:
        raw = pd.read_csv(SNAPSHOT, index_col=0, parse_dates=True)
    return raw.loc[start:end]


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------
def build_series(raw: pd.DataFrame) -> pd.DataFrame:
    """Construct the per-capita series used in the business-cycle-facts table.

    Returns log levels (natural logs) for quantities and the ex-post real rate
    in percentage points (annualized). Column names are the display names.
    """
    pop = raw["population"]  # thousands
    df = pd.DataFrame(index=raw.index)

    # Fernald business-sector output, hours, capital: index levels -> per capita
    df["GDP"] = raw["log_Y_business"] - np.log(pop)
    df["Hours"] = raw["log_hours"] - np.log(pop)
    df["Capital"] = raw["log_capital"] - np.log(pop)

    # Consumption = nondurables + services (per capita, from FRED)
    df["Consumption"] = np.log(raw["C_nondurables_pc"] + raw["C_services_pc"])
    # Investment = private fixed + inventories + consumer durables (per capita $)
    inv_pc = raw["I_private"] * 1e9 / (pop * 1e3)
    df["Investment"] = np.log(inv_pc + raw["C_durables_pc"])

    df["GDP per Hour"] = df["GDP"] - df["Hours"]
    df["Real Wage"] = np.log(raw["real_wage"])

    # Extensive margin = employment / population; intensive = hours / employment
    df["Extensive Margin"] = np.log(raw["employment"] / pop)
    df["Intensive Margin"] = df["Hours"] - df["Extensive Margin"]

    # Ex-post real rate (annualized, percentage points): i_t - 4*dlog(P_t)*100
    infl = 400 * np.log(raw["gdp_deflator"]).diff()
    df["Real Rate"] = raw["tbill"] - infl

    # Solow residual (per-capita normalization cancels because shares sum to 1)
    df["TFP"] = df["GDP"] - ALPHA * df["Capital"] - (1 - ALPHA) * df["Hours"]

    df["recession"] = raw["recession"]
    return df.dropna()


# Series measured in percentage points rather than logs.
LEVEL_SERIES = ["Real Rate"]


# ---------------------------------------------------------------------------
# Detrending and moments
# ---------------------------------------------------------------------------
def hp_cycles(df: pd.DataFrame, lam: float = 1600) -> tuple[pd.DataFrame, pd.DataFrame]:
    """HP-filter every column (except the recession dummy).

    Returns (cycle, trend). Log series are multiplied by 100 so that the cycle
    is in percent deviations from trend; Real Rate stays in percentage points.
    """
    cyc, trd = {}, {}
    for col in df.columns.drop("recession", errors="ignore"):
        scale = 1.0 if col in LEVEL_SERIES else 100.0
        c, t = hpfilter(df[col], lamb=lam)
        cyc[col], trd[col] = scale * c, t
    return pd.DataFrame(cyc), pd.DataFrame(trd)


def bc_moments(cycles: pd.DataFrame, ref: str = "GDP") -> pd.DataFrame:
    """Standard deviation, relative SD, correlation with GDP, first-order autocorrelation."""
    return pd.DataFrame({
        "SD (%)": cycles.std(),
        "SD / SD(GDP)": cycles.std() / cycles[ref].std(),
        "Corr(x, GDP)": cycles.corrwith(cycles[ref]),
        "Corr(x_t, x_t-1)": cycles.apply(lambda s: s.autocorr(1)),
    })


def recession_periods(rec: pd.Series) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """List of (start, end) dates of NBER recessions from a 0/1 quarterly series."""
    rec = rec.fillna(0).astype(int)
    d = rec.diff().fillna(rec.iloc[0])
    starts = rec.index[d == 1]
    ends = rec.index[d == -1]
    if len(ends) < len(starts):
        ends = ends.append(pd.DatetimeIndex([rec.index[-1]]))
    return list(zip(starts, ends))


def shade_recessions(ax, rec: pd.Series, **kw):
    """Add grey bars for NBER recessions to a matplotlib axis."""
    for s, e in recession_periods(rec):
        ax.axvspan(s, e, color=kw.get("color", "0.88"), lw=0, zorder=0)


# ---------------------------------------------------------------------------
# Plot style (shared across lectures)
# ---------------------------------------------------------------------------
COLORS = {"gdp": "#2a78d6", "series": "#eb6834", "trend": "#6b6a64", "text": "#3a3a37"}


def set_plot_style():
    """Light, recessive axes; thin lines. Call once at the top of a notebook."""
    import matplotlib as mpl
    mpl.rcParams.update({
        "figure.dpi": 110, "figure.figsize": (8, 4.5),
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "0.6", "axes.labelcolor": COLORS["text"],
        "axes.grid": True, "grid.color": "0.92", "grid.linewidth": 0.8,
        "xtick.color": "0.4", "ytick.color": "0.4",
        "lines.linewidth": 1.6, "legend.frameon": False, "font.size": 10,
        "axes.titlesize": 11, "axes.titleweight": "bold",
    })
