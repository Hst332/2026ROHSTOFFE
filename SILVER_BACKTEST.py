import yfinance as yf
import numpy as np
import pandas as pd

from model_core import model_score

# ==================================================
# CONFIG (Silver-spezifisch)
# ==================================================

TICKER = "SI=F"
PERIOD = "6y"
LOOKBACK = 40          # exakt ausreichend für Score-V2
HOLD_DAYS = 10         # Silver hält länger
MIN_ROWS = 500

THRESHOLDS = [0.19, 0.30, 0.72, 0.74, 0.68]

# ==================================================
# LOAD DATA
# ==================================================

print("[START] Silver backtest")

df = yf.download(
    TICKER,
    period=PERIOD,
    interval="1d",
    progress=False
).dropna()

print("Downloaded rows:", len(df))

if len(df) < MIN_ROWS:
    raise RuntimeError("Not enough data for Silver backtest")

# ==================================================
# BACKTEST LOOP (FIXED LOOKBACK – IMPORTANT)
# ==================================================

scores = []
future_returns = []

for i in range(LOOKBACK, len(df) - HOLD_DAYS):
    window = df.iloc[i - LOOKBACK : i]   # <<< DER ENTSCHEIDENDE FIX
    score = model_score(window)

    entry = df["Close"].iloc[i]
    exit_ = df["Close"].iloc[i + HOLD_DAYS]

    ret = (exit_ - entry) / entry

    scores.append(score)
    future_returns.append(ret)

scores = np.array(scores)
future_returns = np.array(future_returns)

# ==================================================
# THRESHOLD EVALUATION
# ==================================================

rows = []

for th in THRESHOLDS:
    mask = scores >= th
    trades = int(mask.sum())

    if trades == 0:
        acc = 0.0
        profit = 0.0
    else:
        acc = (future_returns[mask] > 0).mean() * 100
        profit = future_returns[mask].sum()

    print(
        f"TH={th:.2f} | "
        f"Trades={trades} | "
        f"Accuracy={acc:.2f}% | "
        f"Profit={profit:.1f}"
    )

    rows.append((th, trades, round(acc, 2), round(profit, 1)))

# ==================================================
# SAVE RESULTS
# ==================================================

pd.DataFrame(
    rows,
    columns=["threshold", "trades", "accuracy_pct", "profit_sum"]
).to_csv("silver_backtest_results.csv", index=False)

print("[OK] silver_backtest_results.csv written")
