import numpy as np
import pandas as pd


def model_score(df) -> float:
    close = df["Close"]

    # Robust gegen Series ODER DataFrame
    if isinstance(close, pd.DataFrame):
        last = float(close.iloc[-1, 0])
        past = float(close.iloc[-21, 0])
    else:
        last = float(close.iloc[-1])
        past = float(close.iloc[-21])

    r = (last - past) / past

    raw = 0.5 + np.clip(r * 3.0, -0.2, 0.2)
    return round(float(np.clip(raw, 0.30, 0.70)), 3)
