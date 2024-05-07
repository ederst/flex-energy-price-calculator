import sys
from datetime import date

from flex_energy_price_calculator.models.base import DEFAULT_CACHE_DIR


def main():
    if len(sys.argv) != 3:
        print("Usage: <YYYY-MM> <model>")
        exit(1)
    month = sys.argv[1]
    model = sys.argv[2]

    display_date = date.fromisoformat(f"{month}-01")

    DEFAULT_CACHE_DIR.mkdir(exist_ok=True)

    print(f"Unknown model: {model}")
    exit(1)

    print("stock prices:", model.prices)
    print(f"avg stock price:     {model.average_price:5.2f}€/MWh")
    print("---")
    print(f"msg: {model.status_message}")
    print(f"net enduser price:   {model.net_price:5.2f}ct/KWh")
    print(f"gross enduser price: {model.gross_price:5.2f}ct/KWh")


if __name__ == "__main__":
    main()
