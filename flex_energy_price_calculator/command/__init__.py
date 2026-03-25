import sys
from datetime import date

from flex_energy_price_calculator.models.base import DEFAULT_CACHE_DIR
from flex_energy_price_calculator.models.gogreenenergy.gogreenenergyflex import (
    GoGreenEnergyFlex,
    GoGreenEnergyFlexFuture,
)
from flex_energy_price_calculator.models.noprovider.lastmonthavg import LastMonthAvg
from flex_energy_price_calculator.models.fullmonth.fullmonth import FullMonth
from flex_energy_price_calculator.models.oekostrom.oekoflow import OekoFlow10
from dateutil.relativedelta import relativedelta


def main():
    if len(sys.argv) != 4:
        print("Usage: <YYYY-MM> <YYYY-MM> <model>")
        exit(1)
    start_month = sys.argv[1]
    end_month = sys.argv[2]
    model_arg = sys.argv[3]

    print(f"Calculating prices for {start_month} to {end_month}\n---")

    DEFAULT_CACHE_DIR.mkdir(exist_ok=True)

    start_date = date.fromisoformat(f"{start_month}-01")
    end_date = date.fromisoformat(f"{end_month}-01")
    current_date = start_date
    display_model = {
        'prices': [],
        'average_prices': [],
        'status_messages': [],
        'net_prices': [],
        'gross_prices': [],
    }
    while current_date <= end_date:
        if model_arg == "oekoflow1.0":
            model = OekoFlow10(current_date)
        elif model_arg in ["gogreenenergyflex", "gogreenenergyflexplus"]:
            model = GoGreenEnergyFlex(current_date)
        elif model_arg in ["gogreenenergyflexfuture", "gogreenenergyflexfutureplus"]:
            model = GoGreenEnergyFlexFuture(current_date)
        elif model_arg in ["lmavg"]:
            model = LastMonthAvg(current_date)
        elif model_arg == "fullmonth":
            model = FullMonth(current_date)
        else:
            print(f"Unknown model: {model_arg}")
            exit(1)

        display_model['prices'].extend(model.prices)
        display_model['average_prices'].append(model.average_price)
        display_model['status_messages'].append(model.status_message),
        display_model['net_prices'].append(model.net_price),
        display_model['gross_prices'].append(model.gross_price),
        current_date = current_date + relativedelta(months=1)


    average_price = sum(display_model['average_prices']) / len(display_model['average_prices'])
    net_price = sum(display_model['net_prices']) / len(display_model['net_prices'])
    gross_price = sum(display_model['gross_prices']) / len(display_model['gross_prices'])

    prices_string = "".join([f"\n  - {x[0]}: {x[1]}" for x in display_model['prices']])

    print(
        (
            f"stock prices: {prices_string}\n"
            f"avg stock price: {average_price:5.2f}€/MWh\n"
            "---\n"
            # f"msg: {model.status_message}\n"
            f"net enduser price:   {net_price:5.2f}ct/KWh\n"
            f"gross enduser price: {gross_price:5.2f}ct/KWh\n"
        )
    )




if __name__ == "__main__":
    main()
