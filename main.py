from forecast_assets import run_all
from forecast_writer import write_daily_summary

from trade_tracker import record_signals, evaluate_open_trades


ASSET_TO_TICKER = {
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "NATURAL GAS": "NG=F",
    "COPPER": "HG=F",
}


def main():
    results = run_all()

    # 1) heutige handelbare Signale loggen (LONG/SHORT, nur DATA_OK)
    record_signals(results, ASSET_TO_TICKER)

    # 2) offene Trades auswerten (z.B. 5 Tradingdays später)
    stats = evaluate_open_trades(ASSET_TO_TICKER, horizon_days=5)

    # 3) Output schreiben inkl. Stats
    write_daily_summary(results, stats)


if __name__ == "__main__":
    main()
