import os
from datetime import datetime

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "forecast_output.txt")


def write_daily_summary(results):

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        f.write(f"Run time (UTC): {datetime.utcnow():%Y-%m-%d %H:%M:%S}\n")
        f.write("=" * 170 + "\n")
        f.write(
            "ASSET         CLOSE     SCORE   SIGNAL       1-5D      2-3W      "
            "GPT 1-5D   GPT 2-3W   FINAL           "
            "DATA_OK  LAST_BAR_UTC        AGE_s  AGE_h  ROWS  NAN_LAST  STALE  ZUSATZINFO\n"
        )
        f.write("-" * 170 + "\n")

        for r in results:

            close = r.get("close")
            close_str = f"{close:>7.1f}" if isinstance(close, (int, float)) else f"{'NA':>7}"

            data_ok = r.get("data_ok", False)
            final = r.get("final", "NO_TRADE")

            if not data_ok:
                final = "NO_TRADE(DATA)"

            f.write(
                f"{r.get('asset','NA'):<13}"
                f"{close_str}    "
                f"{r.get('score', 0.0):>5.3f}   "
                f"{r.get('signal', 'NA'):<11}"
                f"{r.get('f_1_5', 0.0):<9}"
                f"{r.get('f_2_3', 0.0):<9}"
                f"{r.get('gpt_1_5d', 'NA'):<10}"
                f"{r.get('gpt_2_3w', 'NA'):<11}"
                f"{final:<14}   "
                f"{str(data_ok):<6}  "
                f"{r.get('last_bar_utc_display','NA'):<16}  "
                f"{r.get('age_s',0):>5}  "
                f"{r.get('age_h',0):>5}  "
                f"{r.get('rows',0):>4}  "
                f"{r.get('nan_last',0):>8}  "
                f"{r.get('stale',0):>5}  "
                f"{r.get('zusatzinfo','')}\n"
            )

        f.write("=" * 170 + "\n")
