from datetime import datetime

def write_daily_summary(results):
    with open("forecast_output.txt", "w") as f:
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
