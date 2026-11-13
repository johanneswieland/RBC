"""Plotting helpers for the continuous-time RBC model (Lecture 3): phase diagrams,
labor-market diagrams, and impulse-response panels. All quantities are log deviations
from the initial steady state in percent; time is in years in the model and shown in quarters.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

import rbc_ct as rbc
from bcdata import COLORS

LOCUS = COLORS["gdp"]          # both loci in one colour, labelled directly (as in Figure 2.1 of the notes)
LOCUS_K = LOCUS_L = LOCUS
ARM = "#2e8b57"                # stable arm
PATH = COLORS["series"]        # equilibrium path
GUIDE = "0.55"
ARROW_PT = 18                  # length of the quadrant arrows in points                 # dotted guide lines, quadrant arrows


def _window(points, center, pad=1.35, floor=0.5):
    """Axis limits centred on `center` that contain all points with some padding."""
    pts = np.asarray(points)
    hk = max(np.abs(pts[:, 0] - center[0]).max() * pad, floor)
    hl = max(np.abs(pts[:, 1] - center[1]).max() * pad, floor)
    return (center[0] - hk, center[0] + hk, center[1] - hl, center[1] + hl)


def _norm(lim, k, l):
    kmin, kmax, lmin, lmax = lim
    return (np.asarray(k) - kmin) / (kmax - kmin), (np.asarray(l) - lmin) / (lmax - lmin)


def _end_label(ax, x, y, text, lim, color, taken, fracs=(0.96, 0.8, 0.65, 0.2, 0.05),
               offset=(0, 6), ha="right", va="bottom"):
    """Write `text` next to the curve (x, y) at the first fraction of its visible part
    (0 = left end) where the label stays inside the axes and does not overlap anything in
    `taken`: points (u, v) or label boxes (u0, v0, u1, v1), all in axes coordinates."""
    u_, v_ = _norm(lim, x, y)
    inside = np.where((u_ >= 0.02) & (u_ <= 0.98) & (v_ >= 0.05) & (v_ <= 0.95))[0]
    if not len(inside):
        return
    renderer = ax.figure.canvas.get_renderer()
    to_axes = ax.transAxes.inverted()

    def clash(box):
        u0, v0, u1, v1 = box
        bad = 0.0
        if u0 < 0 or u1 > 1 or v0 < 0 or v1 > 1:
            bad += 1.0
        for t in taken:
            if len(t) == 2:
                if u0 - 0.01 < t[0] < u1 + 0.01 and v0 - 0.02 < t[1] < v1 + 0.02:
                    bad += 1.0
            else:
                ou = min(u1, t[2]) - max(u0, t[0]); ov = min(v1, t[3]) - max(v0, t[1])
                if ou > -0.01 and ov > -0.01:
                    bad += 1.0 + max(ou, 0) * max(ov, 0) * 100
        return bad

    best = None
    for f in fracs:
        i = inside[int(round(f * (len(inside) - 1)))]
        h = "left" if f < 0.5 else "right"
        off = (abs(offset[0]) + 4 if h == "left" else -abs(offset[0]), offset[1])
        ann = ax.annotate(text, (x[i], y[i]), xytext=off, textcoords="offset points", ha=h, va=va,
                          color=color, fontsize=10)
        ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3])
        (u0, v0), (u1, v1) = to_axes.transform(ann.get_window_extent(renderer).get_points())
        box = (u0, v0, u1, v1)
        c = clash(box)
        if best is None or c < best[0]:
            if best is not None:
                best[1].remove()
            best = (c, ann, box)
        else:
            ann.remove()
        if c == 0:
            break
    taken.append(best[2])


def _quadrant_arrows(ax, A, forcings, lim, avoid):
    """In each of the four regions cut out by the loci (signs of k_dot and lambda_dot), a pair of
    arrows showing the direction in which k_hat (horizontal) and lambda_hat (vertical) move there.
    With several forcing vectors (original and shifted loci), arrows are only placed where the
    directions are the same under all of them, so they are correct under either set of loci.
    Each pair is put at the grid point of its region farthest from the curves in `avoid`."""
    kmin, kmax, lmin, lmax = lim
    wk, wl = kmax - kmin, lmax - lmin
    g = np.linspace(0.06, 0.94, 23)
    U, V = np.meshgrid(g, g)
    K, L = kmin + U * wk, lmin + V * wl
    SK = [np.sign(A[0, 0] * K + A[0, 1] * L + s[0]) for s in forcings]
    SL = [np.sign(A[1, 0] * K + A[1, 1] * L + s[1]) for s in forcings]
    pts = np.concatenate([np.column_stack(_norm(lim, c[0], c[1])) for c in avoid])
    dist = np.min(np.hypot(U.ravel()[:, None] - pts[:, 0], V.ravel()[:, None] - pts[:, 1]), axis=1).reshape(U.shape)
    for sk in (1, -1):
        for sl in (1, -1):
            m = np.logical_and.reduce([(a == sk) & (b == sl) for a, b in zip(SK, SL)])
            if not m.any():
                continue
            d = np.where(m, dist, -1)
            j = np.unravel_index(np.argmax(d), d.shape)
            # corner in data coordinates, arrows of equal on-screen length (in points)
            for off in [(sk * ARROW_PT, 0), (0, sl * ARROW_PT)]:
                ax.annotate("", xy=(K[j], L[j]), xytext=off, textcoords="offset points",
                            arrowprops=dict(arrowstyle="<|-", color=GUIDE, lw=1.2, mutation_scale=10,
                                            shrinkA=0, shrinkB=0))


def _arrows_along(ax, k, l, lim, fracs=(0.2, 0.5, 0.8), color=PATH):
    """Arrowheads along the curve (k, l) at given fractions of its length (in screen proportions)."""
    kmin, kmax, lmin, lmax = lim
    x, y = (np.asarray(k) - kmin) / (kmax - kmin), (np.asarray(l) - lmin) / (lmax - lmin)
    s = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    if s[-1] < 0.03:
        return
    for f in fracs:
        i = min(np.searchsorted(s, f * s[-1]), len(s) - 2)
        ax.annotate("", xy=(k[i + 1], l[i + 1]), xytext=(k[i], l[i]),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=0, mutation_scale=16))


def phase_diagram(ax, p, z=0.0, g=0.0, z_new=None, g_new=None, path=None, t1=None,
                  lim=None, arms=True, quadrants=True, point_labels=None, field=False, pad=None):
    """Phase diagram in (log K, log lambda), drawn in the style of Figure 2.1 of the notes.

    Solid loci: dynamics with forcing (z, g). Dashed loci ("new"): dynamics with forcing
    (z_new, g_new), i.e. while a shock is in effect. The quadrant arrows are placed only where the
    original and the shifted dynamics point in the same direction. path: DataFrame from rbc.irf / rbc.irf_step (log deviations in %).
    t1: date at which a transitory shock ends (marked). For transitory shocks the figure follows
    Figure 2.5 of the notes: the temporarily shifted locus, the stable arm that applies from t1 on,
    and the stable arm if the shock were permanent. point_labels: optional names for the start of
    the path and the final steady state, e.g. ("A", "B"); with t1, three names (start, t1, end).
    pad: half-width of the automatic window relative to the spread of the plotted points.
    Axes are log deviations from the initial steady state; ticks mark only named points.
    """
    A, B = rbc.linear_system(p)
    shock = z_new is not None
    zf, gf = (z_new, g_new) if shock else (z, g)
    s = B @ np.array([zf, gf]) * 100
    xs_old = -np.linalg.solve(A, B @ np.array([z, g])) * 100
    xs_new = -np.linalg.solve(A, s) if shock else xs_old           # steady state of impact dynamics
    permanent = shock and t1 is None
    xs_end = xs_new if permanent else xs_old

    if lim is None:
        pts = [xs_old] + ([xs_new] if permanent or path is None else [])
        if path is not None:
            pts += list(path[["K", "lambda"]].values)
        pts = np.array(pts)
        if shock and t1 is not None:
            # transitory shock: show the path, the old steady state and the temporary steady state
            # (where the shifted loci cross) with room around them for all four quadrant arrows
            # also the crossings of old with shifted loci: they bound the regions in which the
            # old and the temporary dynamics agree (where the quadrant arrows go)
            s_old_ = B @ np.array([z, g]) * 100
            cross = [-np.linalg.solve(A[[0, 1]], np.array([sa[0], sb[1]]))
                     for sa, sb in [(s_old_, s), (s, s_old_)]]
            cross = [c for c in cross if np.abs(c - xs_old).max() > 1e-9 and np.abs(c - xs_new).max() > 1e-9]
            pts = np.vstack([pts, xs_new] + cross)
            lo, hi = pts.min(axis=0), pts.max(axis=0)
            m = (pad or (0.35 if not cross else 0.25)) * (hi - lo)
            lim = (lo[0] - m[0], hi[0] + m[0], lo[1] - m[1], hi[1] + m[1])
        else:
            if path is not None and not shock:
                center = xs_end
            else:
                center = 0.5 * (pts.min(axis=0) + pts.max(axis=0))
            lim = _window(pts, center, pad=pad or (1.35 if not shock else 1.8))
    kmin, kmax, lmin, lmax = lim
    kgrid = np.linspace(kmin, kmax, 200)
    taken = [_norm(lim, *xs_old)]                       # label spots already used (axes coords)
    if path is not None:
        idx = np.linspace(0, len(path) - 1, 12).astype(int)
        taken += [_norm(lim, path["K"].iloc[i], path["lambda"].iloc[i]) for i in idx]
    if permanent:
        taken.append(_norm(lim, *xs_new))
    curves = []                                         # curves the quadrant arrows should avoid

    if field:
        kk, ll = np.meshgrid(np.linspace(kmin, kmax, 25), np.linspace(lmin, lmax, 25))
        ax.streamplot(kk, ll, A[0, 0] * kk + A[0, 1] * ll + s[0], A[1, 0] * kk + A[1, 1] * ll + s[1],
                      color="0.88", density=0.7, linewidth=0.6, arrowsize=0.7)

    # loci: one colour, labelled next to the lines
    lines = [rbc.loci(p, kgrid / 100, z, g)]
    if shock:
        lines.append(rbc.loci(p, kgrid / 100, z_new, g_new))
    lines = [100 * y for pair in lines for y in pair]
    for i in range(len(lines)):                         # labels should avoid points where loci cross
        for j in range(i + 1, len(lines)):
            d = lines[i] - lines[j]
            for c in np.where(np.sign(d[:-1]) * np.sign(d[1:]) < 0)[0]:
                taken.append(_norm(lim, kgrid[c], lines[i][c]))
    lam_lab = dict(fracs=(0.93, 0.8, 0.65), offset=(7, 0), ha="left", va="center")
    k0, l0 = rbc.loci(p, kgrid / 100, z, g)
    for y, lab, kw in [(k0, r"$\dot{\hat k}_t=0$", {}), (l0, r"$\dot{\hat\lambda}_t=0$", lam_lab)]:
        ax.plot(kgrid, 100 * y, color=LOCUS, lw=1.8)
        _end_label(ax, kgrid, 100 * y, lab, lim, LOCUS, taken, **kw)
        curves.append((kgrid, 100 * y))
    if shock:
        k1, l1 = rbc.loci(p, kgrid / 100, z_new, g_new)
        tag = "(new)" if t1 is None else "(until $t_1$)"
        for y, y0, lab, kw in [(k1, k0, r"$\dot{\hat k}_t=0$ " + tag, {}),
                               (l1, l0, r"$\dot{\hat\lambda}_t=0$ " + tag, lam_lab)]:
            if not np.allclose(y, y0):
                ax.plot(kgrid, 100 * y, color=LOCUS, lw=1.8, ls="--")
                _end_label(ax, kgrid, 100 * y, lab, lim, LOCUS, taken, **kw)
                curves.append((kgrid, 100 * y))

    if arms:
        mu_s, mu_u, P = rbc.saddle(A)
        slope_s, slope_u = P[1, 0] / P[0, 0], P[1, 1] / P[0, 1]
        ys = xs_end[1] + slope_s * (kgrid - xs_end[0])
        ax.plot(kgrid, ys, color=ARM, lw=1.4, ls=(0, (6, 3)))
        arm_name = "new stable arm" if permanent else ("stable arm at $t_1$" if shock else "stable arm")
        _end_label(ax, kgrid, ys, arm_name, lim, ARM, taken,
                   fracs=(0.04, 0.2, 0.8, 0.96), offset=(8, 0), ha="left", va="center")
        curves.append((kgrid, ys))
        if shock and t1 is not None:                  # stable arm if the shock were permanent
            yp = xs_new[1] + slope_s * (kgrid - xs_new[0])
            ax.plot(kgrid, yp, color=ARM, lw=1.4, ls=":")
            _end_label(ax, kgrid, yp, "stable arm if shock permanent", lim, ARM, taken,
                       fracs=(0.97, 0.8), offset=(4, -8), ha="right", va="top")
            curves.append((kgrid, yp))
        if not shock:
            yu = xs_end[1] + slope_u * (kgrid - xs_end[0])
            ax.plot(kgrid, yu, color="0.65", lw=1.0, ls=":")
            _end_label(ax, kgrid, yu, "unstable arm", lim, "0.5", taken)
            curves.append((kgrid, yu))
    if path is not None:
        curves.append((path["K"].values, path["lambda"].values))
        curves.append((np.full(20, path["K"].iloc[0]), np.linspace(xs_old[1], path["lambda"].iloc[0], 20)))
    if quadrants:
        s_old = B @ np.array([z, g]) * 100
        for t in taken:                                # keep the arrows away from labels too
            us = np.linspace(t[0], t[2], 6) if len(t) == 4 else np.array([t[0]])
            vs = np.full_like(us, 0.5 * (t[1] + t[3])) if len(t) == 4 else np.array([t[1]])
            curves.append((kmin + us * (kmax - kmin), lmin + vs * (lmax - lmin)))
        _quadrant_arrows(ax, A, [s, s_old] if shock else [s], lim, curves)

    # ticks only at named points, with dotted guide lines to the axes
    xt, xl, yt, yl = [xs_old[0]], [r"$\bar K$"], [xs_old[1]], [r"$\bar\lambda$"]
    guides = [xs_old]
    if permanent:
        xt.append(xs_new[0]); xl.append(r"$\bar K'$"); yt.append(xs_new[1]); yl.append(r"$\bar\lambda'$")
        guides.append(xs_new)

    if path is not None:
        K, L = path["K"].values, path["lambda"].values
        start = (K[0], L[0])
        if t1 is None:
            ax.plot(K, L, color=PATH, lw=2.4)
            _arrows_along(ax, K, L, lim)
        else:
            i1 = np.where(path.index.values == t1)[0][0]
            ax.plot(K, L, color=PATH, lw=2.4)
            _arrows_along(ax, K[:i1 + 1], L[:i1 + 1], lim, fracs=(0.5,))
            _arrows_along(ax, K[i1:], L[i1:], lim, fracs=(0.3, 0.7))
            ax.plot(K[i1], L[i1], "s", color=PATH, ms=7, zorder=5)
            lab1 = point_labels[1] if point_labels and len(point_labels) > 2 else r"$t_1$"
            ax.annotate(lab1, (K[i1], L[i1]), xytext=(-6, 6), textcoords="offset points", ha="right",
                        color=PATH, fontsize=11)
            xt.append(K[i1]); xl.append(r"$K_{t_1}$"); yt.append(L[i1]); yl.append(r"$\lambda_{t_1}$")
            guides.append((K[i1], L[i1]))
            xl[0] = r"$\bar K = K_{t_0} = K_\infty$"; yl[0] = r"$\bar\lambda = \lambda_\infty$"
        if abs(K[0] - xs_old[0]) < 1e-9:              # shock: lambda jumps on impact
            ax.annotate("", xy=start, xytext=tuple(xs_old),
                        arrowprops=dict(arrowstyle="-|>", color=PATH, lw=1.2, ls=":", mutation_scale=12))
            yt.append(L[0]); yl.append(r"$\lambda_{t_0}$")
            ax.plot([kmin, K[0]], [L[0], L[0]], color=GUIDE, lw=0.7, ls=":")
        else:                                         # initial condition off the steady state
            xt.append(K[0]); xl.append(r"$K_0$"); yt.append(L[0]); yl.append(r"$\lambda_0$")
            guides.append(start)
        ax.plot(*start, "o", color=PATH, ms=8, zorder=5)
        lab0 = point_labels[0] if point_labels else (r"$t_0$" if shock else None)
        if lab0:
            ax.annotate(lab0, start, xytext=(7, 5), textcoords="offset points", color=PATH, fontsize=11)

    for (gk, gl) in guides:
        ax.plot([gk, gk], [lmin, gl], color=GUIDE, lw=0.7, ls=":")
        ax.plot([kmin, gk], [gl, gl], color=GUIDE, lw=0.7, ls=":")
    ax.plot(*xs_old, "o", color=COLORS["text"], ms=6, zorder=5)
    if permanent:
        ax.plot(*xs_new, "o", mfc="white", mec=COLORS["text"], mew=1.5, ms=7, zorder=5)
    if point_labels:
        ax.annotate(point_labels[-1], tuple(xs_end), xytext=(7, -14), textcoords="offset points",
                    color=COLORS["text"], fontsize=11)

    # drop tick labels that would overlap
    def thin(ticks, labels, span):
        keep_t, keep_l = [], []
        for t_, l_ in zip(ticks, labels):
            if all(abs(t_ - u) > 0.03 * span for u in keep_t):
                keep_t.append(t_); keep_l.append(l_)
        return keep_t, keep_l
    ax.set_xticks(*thin(xt, xl, kmax - kmin)); ax.set_yticks(*thin(yt, yl, lmax - lmin))
    ax.tick_params(length=0, labelsize=11, colors=COLORS["text"])
    ax.set_xlim(kmin, kmax); ax.set_ylim(lmin, lmax)
    ax.set_xlabel(r"capital $K_t$ (log scale)"); ax.set_ylabel(r"marginal utility of wealth $\lambda_t$ (log scale)")
    ax.grid(False)
    return ax


def labor_market(ax, p, path, t=0.0, lim=None, label="impact"):
    """Labor market in (l_hat, w_hat), in %: initial curves and curves at date t of path.

    Labor supply (Lecture 2, (LS) and (HH-FOC)):  w = l/eta - lambda
    Labor demand (Lecture 2, (LD)):               w = z + alpha k - alpha l
    """
    row = path.loc[t]
    row = row.iloc[-1] if row.ndim > 1 else row          # right limit if t appears twice
    if lim is None:                                      # window around the old and new equilibrium
        span = max(abs(row["L"]), abs(row["W"]), 0.2)
        lim = (-1.6 * span, 1.6 * span, -1.6 * span, 1.6 * span)
    lmin, lmax, wmin, wmax = lim
    a, eta = p.alpha, p.eta
    lg = np.linspace(lmin, lmax, 50)
    k, lam, z = row["K"], row["lambda"], row["Z"]
    ax.plot(lg, lg / eta, color=COLORS["gdp"], lw=1.6, label=r"$L^s$ (initial)")
    ax.plot(lg, -a * lg, color=COLORS["series"], lw=1.6, label=r"$L^d$ (initial)")
    if abs(lam) > 1e-9:
        ax.plot(lg, lg / eta - lam, color=COLORS["gdp"], lw=1.6, ls="--", label=fr"$L^s$ ({label})")
    if abs(z + a * k) > 1e-9:
        ax.plot(lg, z + a * k - a * lg, color=COLORS["series"], lw=1.6, ls="--", label=fr"$L^d$ ({label})")
    ax.plot(0, 0, "o", color=COLORS["text"], ms=5)
    ax.plot(row["L"], row["W"], "o", color=PATH, ms=7)
    ax.axhline(0, color="0.8", lw=0.6); ax.axvline(0, color="0.8", lw=0.6)
    ax.set_xlim(lmin, lmax); ax.set_ylim(wmin, wmax)
    ax.set_xlabel(r"hours $\hat l_t$ (%)"); ax.set_ylabel(r"real wage $\hat w_t$ (%)")
    ax.grid(False)
    return ax


IRF_VARS = ["lambda", "K", "C", "L", "Y", "I", "W", "r (p.p.)"]
IRF_TITLES = {"lambda": r"$\lambda$", "K": "K", "C": "C", "L": "L", "Y": "Y", "I": "I", "W": "W",
              "r (p.p.)": "r (p.p. per year)"}


def irf_panel(path, shock, t1=None, quarters=60, axes=None):
    """Impulse responses (% deviations; r in percentage points) against quarters."""
    if axes is None:
        fig, axes = plt.subplots(2, 4, figsize=(14, 5.2))
    q = 4 * path.index.values
    keep = q <= quarters
    for ax, v in zip(np.ravel(axes), IRF_VARS):
        ax.plot(q[keep], path[v].values[keep], color=COLORS["gdp"], lw=2)
        ax.axhline(0, color="0.3", lw=0.7)
        if t1 is not None:
            ax.axvspan(0, 4 * t1, color="0.92", zorder=0)
        ax.set_title(IRF_TITLES[v], fontsize=10)
    for ax in np.ravel(axes)[4:]:
        ax.set_xlabel("quarters")
    return axes


def sign_table(path, t1=None, tol=1e-9):
    """Signs of the responses in the format of the lecture-note tables.

    Impact: change at t0 relative to the initial steady state. Transition: direction of change
    relative to the value at the start of the phase (two arrows = changes direction). At t1: jump
    when the shock ends. Steady state: long-run change relative to the initial steady state.
    """
    import pandas as pd

    def sgn(x):
        return "↑" if x > tol else ("↓" if x < -tol else "0")

    def direction(seg):
        d = np.diff(seg)
        big = np.abs(d) > 1e-12
        if not big.any():
            return "0"
        s = np.sign(d[big])
        if (s > 0).all():
            return "↑"
        if (s < 0).all():
            return "↓"
        return "↑ then ↓" if s[0] > 0 else "↓ then ↑"

    t = path.index.values
    rows = {}
    for v in IRF_VARS:
        x = path[v].values
        if t1 is None:
            rows[v] = [sgn(x[0]), direction(x[1:]), sgn(round(x[-1], 6))]
        else:
            a, b = np.where(t == t1)[0][:2]
            rows[v] = [sgn(x[0]), direction(x[1:a + 1]), sgn(x[b] - x[a]), direction(x[b:]), sgn(round(x[-1], 4))]
    cols = (["impact", "transition", "steady state"] if t1 is None
            else ["impact", "transition I", "at t1", "transition II", "steady state"])
    out = pd.DataFrame(rows, index=cols).T
    out.index = ["λ", "K", "C", "L", "Y", "I", "W", "r"]
    return out
