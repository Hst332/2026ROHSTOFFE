import numpy as np
# decision_engine.py

def decide(asset, score, signal_1_5d, signal_2_3w, macro_bias):
    """
    Lightweight rule-based ChatGPT replacement
    (deterministic & backtest-stable)
    """
    if np.std(score_history[-10:]) < 1e-3:
        raise RuntimeError("SCORE STALLED – TRADING HALTED")
    # GPT-style interpretation
    if signal_1_5d == "++":
        gpt_1_5d = "Bullish"
    elif signal_1_5d == "--":
        gpt_1_5d = "Bearish"
    else:
        gpt_1_5d = "Neutral"

    if signal_2_3w == "++":
        gpt_2_3w = "Bullish"
    elif signal_2_3w == "--":
        gpt_2_3w = "Bearish"
    else:
        gpt_2_3w = "Neutral"

    # FINAL decision logic (asset-agnostic baseline)
    if (
        score >= 0.55
        and signal_1_5d == "++"
        and signal_2_3w == "++"
    ):
        final = "LONG"

    elif (
        score <= 0.45
        and signal_1_5d == "--"
        and signal_2_3w == "--"
    ):
        final = "SHORT"

    else:
        final = "NO_TRADE"

    return {
        "gpt_1_5d": gpt_1_5d,
        "gpt_2_3w": gpt_2_3w,
        "final": final
    }
