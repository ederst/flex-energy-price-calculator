import sys
from datetime import date

from flex_energy_price_calculator.models.base import DEFAULT_CACHE_DIR
from flex_energy_price_calculator.models.gogreenenergy.gogreenenergyflex import (
    GoGreenEnergyFlex,
    GoGreenEnergyFlexFuture,
)
from flex_energy_price_calculator.models.noprovider.lastmonthavg import LastMonthAvg
from flex_energy_price_calculator.models.oekostrom.oekoflow import OekoFlow10


def main():
    if len(sys.argv) != 3:
        print("Usage: <YYYY-MM> <model>")
        exit(1)
    month = sys.argv[1]
    model = sys.argv[2]

    display_date = date.fromisoformat(f"{month}-01")

    DEFAULT_CACHE_DIR.mkdir(exist_ok=True)

    if model == "oekoflow1.0":
        model = OekoFlow10(display_date)
    elif model in ["gogreenenergyflex", "gogreenenergyflexplus"]:
        model = GoGreenEnergyFlex(display_date)
    elif model in ["gogreenenergyflexfuture", "gogreenenergyflexfutureplus"]:
        model = GoGreenEnergyFlexFuture(display_date)
    elif model in ["lmavg"]:
        model = LastMonthAvg(display_date)
    else:
        print(f"Unknown model: {model}")
        exit(1)

    prices_string = "".join([f"\n  - {x[0]}: {x[1]}" for x in model.prices])

    print(
        (
            f"stock prices: {prices_string}\n"
            f"avg stock price: {model.average_price:5.2f}€/MWh\n"
            "---\n"
            f"msg: {model.status_message}\n"
            f"net enduser price:   {model.net_price:5.2f}ct/KWh\n"
            f"gross enduser price: {model.gross_price:5.2f}ct/KWh\n"
        )
    )


if __name__ == "__main__":
    main()
