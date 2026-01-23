import numpy as np
import pandas as pd

def compute_score(prices) -> float:
    """
    SCORE V2 – robust input handling
    Accepts: np.ndarray | pd.Series | pd.DataFrame
    """

    # --- input normalization (CRITICAL FIX) ---
    if isinstance(prices, pd.DataFrame):
        if "Close" in prices.columns:
            p = prices["Close"].values
        else:
            # fallback: last column
            p = prices.iloc[:, -1].values

    elif isinstance(prices, pd.Series):
        p = prices.values

    else:
        p = np.asarray(prices, dtype=float)

    # --- safety ---
    if len(p) < 30:
        return 0.50

    p = p.astype(float)

    # returns
    r_20 = (p[-1] - p[-21]) / p[-21]
    r_5  = (p[-1] - p[-6])  / p[-6]

    # volatility (log-returns)
    rets = np.diff(np.log(p[-21:]))
    vol  = np.std(rets) + 1e-6

    # normalized momentum
    m20 = r_20 / (vol * np.sqrt(20))
    m5  = r_5  / (vol * np.sqrt(5))

    core = (
        0.65 * np.tanh(m20 * 0.8) +
        0.35 * np.tanh(m5  * 1.2)
    )

    score = 0.5 + core * 0.25
    return round(float(score), 3)


# backward compatibility
model_score = compute_score
