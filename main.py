from forecast_assets import run_all
from decision_engine import log_decision

def main():
    results = run_all()

    print("\nDECISION TRACE (single source of truth)")
    print("-" * 80)

    for r in results:
        log_decision(r["asset"], r["score"])

if __name__ == "__main__":
    main()
