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
            close = r.get("close", None)
            close_str = f"{close:>7.1f}" if isinstance(close, (int, float)) else f"{'NA':>7}"

            data_ok = bool(r.get("data_ok", False))

            last_bar_disp = str(r.get("last_bar_utc_display", r.get("last_bar_utc", "NA")))
            age_s = int(r.get("age_s", 10**9)) if str(r.get("age_s", "")).strip() != "" else 10**9
            age_h = float(r.get("age_h", round(age_s / 3600.0, 2)))
            rows = int(r.get("rows", 0)) if str(r.get("rows", "")).strip() != "" else 0
            nan_last = int(r.get("nan_last", 1)) if str(r.get("nan_last", "")).strip() != "" else 1
            stale = int(r.get("stale", 1)) if str(r.get("stale", "")).strip() != "" else 1

            final = r.get("final", "NO_TRADE")

            # HARD SAFETY: If data not OK, force final to NO_TRADE(DATA)
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
                f"{last_bar_disp:<16}  "
                f"{age_s:>5}  "
                f"{age_h:>5.2f}  "
                f"{rows:>4}  "
                f"{nan_last:>8}  "
                f"{stale:>5}  "
                f"{r.get('zusatzinfo', '')}\n"
            )

            if not data_ok:
                reason = r.get("guard_reason", r.get("zusatzinfo", "DATA BLOCK"))
                f.write(f"{'':<13}>>> BLOCKED: {reason}\n")

        f.write("=" * 170 + "\n\n")

        # rules block bleibt unverändert (wie bei dir)
        f.write("TRADING RULES (FINAL – BACKTEST VALIDATED)\n\n")
        f.write(
            "GOLD\n"
            "- Direction: LONG only\n"
            "- Entry: prob_up >= 0.53\n"
            "- Position sizing:\n"
            "    0.53 - 0.55 -> 50 %\n"
            "    >= 0.55     -> 100 %\n"
            "- Holding period: 5-20 trading days\n"
            "- Leverage: max 3-5\n"
            "- No short positions\n\n"
            "SILVER\n"
            "- Direction: LONG only\n"
            "- Entry: prob_up >= 0.69\n"
            "- Trades/year: ~12\n"
            "- Leverage: max 15\n"
            "- Stop-loss: hard -20 %\n"
            "- Ignore all signals below threshold\n\n"
            "COPPER\n"
            "- Direction: LONG only\n"
            "- Entry: prob_up >= 0.56\n"
            "- Trades/year: ~60-150\n"
            "- Leverage: max 5-10\n"
            "- Stop-loss: hard -20 %\n"
            "- No shorts\n\n"
            "NATURAL GAS\n"
            "- Direction: LONG & SHORT\n"
            "- LONG  if prob_up >= 0.56\n"
            "- SHORT if prob_up <= 0.44\n"
            "- Otherwise: NO TRADE\n"
            "- Leverage: max 10\n"
            "- Stop-loss: hard -20 %\n\n"
            "NOT TRADED\n"
            "- Crude Oil (too impulsive / unstable regimes)\n"
        )
