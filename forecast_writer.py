import os
from datetime import datetime

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "forecast_output.txt")

def write_daily_summary(results):
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"Run time (UTC): {datetime.utcnow():%Y-%m-%d %H:%M:%S}\n")
        f.write("=" * 90 + "\n")
        f.write("ASSET         CLOSE     SCORE   SIGNAL       1–5D   2–3W\n")
        f.write("-" * 90 + "\n")

        for r in results:
            f.write(
                f"{r['asset']:<13}"
                f"{r['close']:>7.1f}    "
                f"{r['score']:>5.3f}   "
                f"{r['signal']:<11}"
                f"{r['f_1_5']:<6}"
                f"{r['f_2_3']}\n"
            )


        f.write("=" * 90 + "\n\n")

        f.write("TRADING RULES (FINAL – BACKTEST VALIDATED)\n\n")

        f.write(
            "GOLD\n"
            "- Direction: LONG only\n"
            "- Entry: prob_up ≥ 0.53\n"
            "- Position sizing:\n"
            "    0.53 – 0.55 → 50 %\n"
            "    ≥ 0.55      → 100 %\n"
            "- Holding period: 5–20 trading days\n"
            "- Leverage: max 3–5\n"
            "- No short positions\n\n"
            "ChatGPT Prognose 1-5D": gpt_1_5d,
            "ChatGPT Prognose 2-3W": gpt_2_3w,

            "Final": final

            "SILVER\n"
            "- Direction: LONG only\n"
            "- Entry: prob_up ≥ 0.96\n"
            "- Trades/year: ~12\n"
            "- Leverage: max 15\n"
            "- Stop-loss: hard -20 %\n"
            "- Ignore all signals below threshold\n\n"
            "ChatGPT Prognose 1-5D": gpt_1_5d,
            "ChatGPT Prognose 2-3W": gpt_2_3w,
            "Final": final

            "COPPER\n"
            "- Direction: LONG only\n"
            "- Entry: prob_up ≥ 0.56\n"
            "- Trades/year: ~60–150\n"
            "- Leverage: max 5–10\n"
            "- Stop-loss: hard -20 %\n"
            "- No shorts\n\n"
            "ChatGPT Prognose 1-5D": gpt_1_5d,
            "ChatGPT Prognose 2-3W": gpt_2_3w,
            "Final": final

            "NATURAL GAS\n"
            "- Direction: LONG & SHORT\n"
            "- LONG  if prob_up ≥ 0.56\n"
            "- SHORT if prob_up ≤ 0.44\n"
            "- Otherwise: NO TRADE\n"
            "- Leverage: max 10\n"
            "- Stop-loss: hard -20 %\n\n"
            "ChatGPT Prognose 1–5D": gpt_1_5d,
            "ChatGPT Prognose 2–3W": gpt_2_3w,
            "Final": final

            "NOT TRADED\n"
            "- Crude Oil (too impulsive / unstable regimes)\n"
        )
