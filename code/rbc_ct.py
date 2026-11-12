"""The basic RBC model in continuous time.

Household:  max  int_0^inf e^{-rho t} [ ln C - L^{1+1/eta} / (1+1/eta) ] dt
            s.t. dA/dt = r A + W L - C - T
Firm:       Y = Z K^alpha L^{1-alpha},   dK/dt = I - delta K
Government: G = T (lump-sum taxes, wasteful spending)

Equilibrium dynamics in (K, lambda), where lambda = 1/C is the marginal utility of wealth:

    dK/dt      = Z K^alpha L^{1-alpha} - 1/lambda - G - delta K
    dlambda/dt = lambda * (rho + delta - alpha Z K^{alpha-1} L^{1-alpha})
    L          = [lambda (1-alpha) Z K^alpha]^{1/(1/eta + alpha)}     (labor market)

Time is measured in quarters, so rho and delta are quarterly rates.

Linearized system (hats = log deviations; g = (G - G_ss)/Y_ss):

    d/dt [k, lam]' = A [k, lam]' + B [z, g]'
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Parameters and steady state
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Params:
    alpha: float = 1 / 3     # capital share
    rho: float = 0.01        # discount rate (quarterly): beta = e^{-rho} ~ 0.99
    delta: float = 0.02      # depreciation (quarterly), ~8% per year
    eta: float = 1.0         # Frisch elasticity of labor supply
    sg: float = 0.20         # steady-state G/Y
    Z: float = 1.0           # steady-state TFP

    @property
    def phi(self) -> float:
        """phi = 1/(1/eta + alpha): elasticity of L w.r.t. lambda*W-shifters."""
        return 1.0 / (1.0 / self.eta + self.alpha)


def steady_state(p: Params, Z: float | None = None, G: float | None = None) -> dict:
    """Steady state. If G is None, G is set so that G/Y = p.sg.

    With G given in levels (e.g. after a permanent spending shock) L solves a
    one-dimensional equation, which we solve numerically.
    """
    Z = p.Z if Z is None else Z
    a, rho, d, eta = p.alpha, p.rho, p.delta, p.eta
    r = rho                                         # Euler equation: lambda_dot = 0
    KL = (a * Z / (rho + d)) ** (1 / (1 - a))       # MPK = rho + delta
    YL = Z * KL ** a
    W = (1 - a) * YL
    if G is None:
        cy = 1 - d * a / (rho + d) - p.sg           # C/Y = 1 - I/Y - G/Y
        L = ((1 - a) / cy) ** (eta / (1 + eta))     # L^{1/eta} = W/C  =>  L^{1+1/eta} = (1-a)/(C/Y)
        Y = YL * L
        G = p.sg * Y
    else:
        from scipy.optimize import brentq
        # L^{1/eta} * C = W with C = (YL - d*KL) L - G
        f = lambda L: L ** (1 / eta) * ((YL - d * KL) * L - G) - W
        L = brentq(f, 1e-6, 10.0)
        Y = YL * L
    K = KL * L
    I = d * K
    C = Y - I - G
    return dict(Z=Z, K=K, L=L, Y=Y, C=C, I=I, G=G, W=W, r=r, lam=1 / C)


# ---------------------------------------------------------------------------
# Nonlinear model
# ---------------------------------------------------------------------------
def labor(K, lam, Z, p: Params):
    return (lam * (1 - p.alpha) * Z * K ** p.alpha) ** p.phi


def rhs(K, lam, Z, G, p: Params):
    """(dK/dt, dlambda/dt) of the nonlinear model."""
    L = labor(K, lam, Z, p)
    Y = Z * K ** p.alpha * L ** (1 - p.alpha)
    Kdot = Y - 1 / lam - G - p.delta * K
    lamdot = lam * (p.rho + p.delta - p.alpha * Y / K)
    return Kdot, lamdot


def allocations(K, lam, Z, G, p: Params) -> dict:
    """All endogenous variables given the state (K, lambda) and exogenous (Z, G)."""
    L = labor(K, lam, Z, p)
    Y = Z * K ** p.alpha * L ** (1 - p.alpha)
    C = 1 / lam
    Kdot, _ = rhs(K, lam, Z, G, p)
    return dict(K=K, lam=lam, L=L, Y=Y, C=C, I=Kdot + p.delta * K,
                W=(1 - p.alpha) * Y / L, r=p.alpha * Y / K - p.delta, Z=Z, G=G)


# ---------------------------------------------------------------------------
# Linearization
# ---------------------------------------------------------------------------
def linear_system(p: Params):
    """Analytic matrices A (2x2) and B (2x2) of  x_dot = A x + B s,  x=(k, lam), s=(z, g)."""
    a, rho, d, eta, phi = p.alpha, p.rho, p.delta, p.eta, p.phi
    ss = steady_state(p)
    YK, CK = ss["Y"] / ss["K"], ss["C"] / ss["K"]
    m = 1 + (1 - a) * phi                       # output elasticity w.r.t. z (incl. labor response)
    A = np.array([
        [YK * a * m - d,               YK * (1 - a) * phi + CK],
        [(rho + d) * (1 - a) * phi / eta, -(rho + d) * (1 - a) * phi],
    ])
    B = np.array([
        [YK * m,           -YK],
        [-(rho + d) * m,    0.0],
    ])
    return A, B


def numerical_jacobian(p: Params, eps: float = 1e-6):
    """Finite-difference Jacobian of the nonlinear model in log deviations (check on A, B)."""
    ss = steady_state(p)
    K0, lam0, Z0, G0, Y0 = ss["K"], ss["lam"], ss["Z"], ss["G"], ss["Y"]

    def f(x):  # x = (k, lam, z, g) -> (k_dot, lam_dot) as growth rates
        K, lam = K0 * np.exp(x[0]), lam0 * np.exp(x[1])
        Kdot, lamdot = rhs(K, lam, Z0 * np.exp(x[2]), G0 + Y0 * x[3], p)
        return np.array([Kdot / K, lamdot / lam])

    J = np.column_stack([(f(e) - f(-e)) / (2 * eps) for e in eps * np.eye(4)])
    return J[:, :2], J[:, 2:]


def saddle(A):
    """Eigen-decomposition. Returns (mu_s, mu_u, P) with P's columns = (stable, unstable) eigenvectors."""
    mu, P = np.linalg.eig(A)
    order = np.argsort(mu.real)
    mu, P = mu.real[order], P.real[:, order]
    assert mu[0] < 0 < mu[1], "not a saddle"
    return mu[0], mu[1], P


def stable_arm_slope(p: Params) -> float:
    """nu in lam = nu * k along the saddle path."""
    _, _, P = saddle(linear_system(p)[0])
    return P[1, 0] / P[0, 0]


def loci(p: Params, k, z=0.0, g=0.0):
    """lam values on the k_dot = 0 and lam_dot = 0 loci for a grid of k (linearized)."""
    A, B = linear_system(p)
    s = np.array([z, g])
    kdot0 = -(A[0, 0] * k + B[0] @ s) / A[0, 1]
    lamdot0 = -(A[1, 0] * k + B[1] @ s) / A[1, 1]
    return kdot0, lamdot0


# ---------------------------------------------------------------------------
# Impulse responses (linearized, closed form)
# ---------------------------------------------------------------------------
def irf(p: Params, z0=0.0, g0=0.0, theta_z=0.0, theta_g=0.0, T=60, n=601, k0=0.0) -> pd.DataFrame:
    """Linearized response to unanticipated shocks at t=0:

        z(t) = z0 exp(-theta_z t),   g(t) = g0 exp(-theta_g t).

    theta = 0 is a permanent shock. Solution: decompose x into stable/unstable
    components w = P^{-1} x. The unstable component is solved forward (it must stay
    bounded), the stable one backward from the predetermined capital stock k(0)=k0.
    """
    A, B = linear_system(p)
    mu_s, mu_u, P = saddle(A)
    Pinv = np.linalg.inv(P)
    t = np.linspace(0, T, n)
    w_s = np.zeros_like(t)
    w_u = np.zeros_like(t)
    for s0, th, col in [(z0, theta_z, 0), (g0, theta_g, 1)]:
        b = Pinv @ B[:, col] * s0          # loading of this shock on (stable, unstable)
        # forward solution of  w_u' = mu_u w_u + b_u e^{-th t}
        w_u += -b[1] * np.exp(-th * t) / (mu_u + th)
        # particular solution of the stable block (homogeneous part added below)
        w_s += b[0] * np.exp(-th * t) / (-(mu_s + th)) if not np.isclose(mu_s + th, 0) else b[0] * t * np.exp(mu_s * t)
    # pick the homogeneous stable term so that k(0) = k0
    ws0_needed = (k0 - P[0, 1] * w_u[0]) / P[0, 0]
    w_s += (ws0_needed - w_s[0]) * np.exp(mu_s * t)
    x = P @ np.vstack([w_s, w_u])
    k, lam = x
    z = z0 * np.exp(-theta_z * t)
    g = g0 * np.exp(-theta_g * t)
    return derived(p, t, k, lam, z, g)


def derived(p: Params, t, k, lam, z, g) -> pd.DataFrame:
    """Log deviations (x100 = %) of all variables from the linearized state (k, lam, z, g)."""
    a, phi, rho, d = p.alpha, p.phi, p.rho, p.delta
    ss = steady_state(p)
    l = phi * (lam + z + a * k)
    y = z + a * k + (1 - a) * l
    c = -lam
    A, B = linear_system(p)
    kdot = A[0, 0] * k + A[0, 1] * lam + B[0, 0] * z + B[0, 1] * g
    i = (kdot + d * k) / d                       # dI/I = (dK_dot + delta dK)/(delta K)
    w = y - l
    r = (rho + d) * (y - k)                      # dr = d(MPK) = (rho+delta)(y-k), quarterly rate
    df = pd.DataFrame({"K": k, "lambda": lam, "C": c, "L": l, "Y": y, "I": i, "W": w,
                       "Z": z, "G/Y": g}, index=pd.Index(t, name="t")) * 100
    df["r (ann. p.p.)"] = 400 * r                # annualized, percentage points
    return df


# ---------------------------------------------------------------------------
# Nonlinear transition (to verify the linear solution)
# ---------------------------------------------------------------------------
def nonlinear_path(p: Params, Zpath, Gpath, T=200, n=2001):
    """Perfect-foresight nonlinear transition from the old steady state after an
    unanticipated change in the paths Z(t), G(t) (callables). Solved as a two-point
    boundary value problem: K(0) = K_ss (predetermined) and lambda(T) = new steady state.
    """
    from scipy.integrate import solve_bvp

    ss0 = steady_state(p)
    ssT = steady_state(p, Z=Zpath(T), G=Gpath(T))
    t = np.linspace(0, T, n)

    def f(t, x):     # x = (log K, log lambda)
        K, lam = np.exp(x[0]), np.exp(x[1])
        Kdot, lamdot = rhs(K, lam, Zpath(t), Gpath(t), p)
        return np.vstack([Kdot / K, lamdot / lam])

    def bc(x0, xT):
        return np.array([x0[0] - np.log(ss0["K"]), xT[1] - np.log(ssT["lam"])])

    guess = np.vstack([np.log(ss0["K"]) + (np.log(ssT["K"]) - np.log(ss0["K"])) * (1 - np.exp(-0.05 * t)),
                       np.full_like(t, np.log(ssT["lam"]))])
    sol = solve_bvp(f, bc, t, guess, tol=1e-8, max_nodes=200000)
    if not sol.success:
        raise RuntimeError(sol.message)
    K, lam = np.exp(sol.sol(t))
    al = allocations(K, lam, Zpath(t), Gpath(t), p)
    return pd.DataFrame(al, index=pd.Index(t, name="t")), ss0
