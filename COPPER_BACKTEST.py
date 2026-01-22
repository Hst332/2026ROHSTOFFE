# =======================
# COPPER BACKTEST – PHASE 2
# (Gold-Setup + ret_20)
# =======================

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# =======================
# CONFIG
# =======================
SYMBOL = "HG=F"          # Copper Futures
START_DATE = "2010-01-01"

THRESHOLDS = [
    0.50,
    0.52,
    0.54,
    0.56,
    0.58,
    0.60
]

# =======================
# DATA
# =======================
def load_copper():
    df = yf.download(SYMBOL, start=START_DATE, progress=False)

    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    # Features (Gold + Momentum-Erweiterung)
    df["ret_1"] = df["Close"].pct_change(1)
    df["ret_5"] = df["Close"].pct_change(5)
    df["ret_20"] = df["Close"].pct_change(20)      # <<< PHASE 2 FEATURE
    df["ma_10"] = df["Close"].rolling(10).mean()
    df["ma_50"] = df["Close"].rolling(50).mean()
    df["ma_ratio"] = df["ma_10"] / df["ma_50"] - 1
    df["vol_10"] = df["ret_1"].rolling(10).std()

    # Target: nächster Tag höher?
    df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

    df = df.dropna()
    return df

# =======================
# MODEL
# =======================
def fit_model(df):
    features = [
        "ret_1",
        "ret_5",
        "ret_20",     # <<< NEU
        "ma_ratio",
        "vol_10"
    ]

    X = df[features].values
    y = df["Target"].values

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = LogisticRegression(
        max_iter=300,
        class_weight="balanced",
        solver="lbfgs"
    )

    model.fit(Xs, y)

    probs = model.predict_proba(Xs)[:, 1]
    df = df.copy()
    df["prob_up"] = probs

    return df

# =======================
# BACKTEST (LONG ONLY)
# =======================
def backtest(df, threshold):
    trades = []

    for _, row in df.iterrows():
        val = row["prob_up"]
        prob = float(val.iloc[0] if hasattr(val, "iloc") else val)
        target = int(row["Target"])

        if prob >= threshold:
            # LONG trade
            ret = 1 if target == 1 else -1
            trades.append(ret)

    if len(trades) == 0:
        return {
            "threshold": threshold,
            "trades": 0,
            "accuracy": 0.0,
            "profit": 0
        }

    trades = np.array(trades)

    return {
        "threshold": threshold,
        "trades": len(trades),
        "accuracy": trades[trades > 0].size / trades.size,
        "profit": int(trades.sum())
    }

# =======================
# MAIN
# =======================
def main():
    print("[START] Copper backtest (Phase 2 – Gold-Setup + ret_20)")

    df = load_copper()
    df = fit_model(df)

    results = []

    for th in THRESHOLDS:
        res = backtest(df, th)
        results.append(res)

        print(
            f"TH={th:.2f} | "
            f"Trades={res['trades']} | "
            f"Accuracy={res['accuracy']*100:.2f}% | "
            f"Profit={res['profit']}"
        )

    out = pd.DataFrame(results)
    out.to_csv("copper_backtest_phase2_results.csv", index=False)

    print("\n[OK] copper_backtest_phase2_results.csv written")

# =======================
if __name__ == "__main__":
    main()
