import yfinance as yf
import numpy as np
import pandas as pd

from model_core import model_score

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

TICKER = "SI=F"
PERIOD = "6y"          # stabiler als 10y
HOLD_DAYS = 10         # Silver: etwas länger halten
MIN_BARS = 40

THRESHOLDS = [0.90, 0.93, 0.95, 0.96, 0.97]

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print("[START] Silver backtest")

df = yf.download(
    TICKER,
    period=PERIOD,
    interval="1d",
    progress=False
)

df = df.dropna()

print("Downloaded rows:", len(df))

if len(df) < 500:
    raise RuntimeError("Not enough data for Silver backtest")

# --------------------------------------------------
# BACKTEST LOOP
# --------------------------------------------------

scores = []
future_returns = []

for i in range(MIN_BARS, len(df) - HOLD_DAYS):
    window = df.iloc[:i]

    score = model_score(window)

    entry = df["Close"].iloc[i]
    exit_ = df["Close"].iloc[i + HOLD_DAYS]

    ret = (exit_ - entry) / entry

    scores.append(score)
    future_returns.append(ret)

scores = np.array(scores)
future_returns = np.array(future_returns)

# --------------------------------------------------
# THRESHOLD EVALUATION
# --------------------------------------------------

rows = []

for th in THRESHOLDS:
    mask = scores >= th
    trades = int(mask.sum())

    if trades == 0:
        acc = 0.0
        profit = 0.0
    else:
        acc = (future_returns[mask] > 0).mean() * 100
        profit = f
