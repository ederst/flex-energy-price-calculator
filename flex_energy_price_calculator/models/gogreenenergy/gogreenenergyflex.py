from datetime import date, timedelta
from statistics import mean

from ..base import CONVERSION_FACTOR, STD_PROFILE_FACTOR, TAXES, get_eex_close_price

START_DAY = 21
END_DAY = 20
FEES = 9.75
FUTURE_FEES = 14.75

OPTION_ROOT = "E.ATBM"  # EX Phelix AT Future Monthly Base


class GoGreenEnergyFlex:

    def __init__(self, display_date: date, fees: float = FEES) -> None:
        # limit the end date to today
        end_date = min(
            (display_date - timedelta(days=1)).replace(day=END_DAY),
            date.today() - timedelta(days=1),
        )
        start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=START_DAY)

        delta_days = (end_date - start_date).days
        all_days = [end_date - timedelta(days=i) for i in range(delta_days + 1)]

        business_days = [d for d in all_days if d.weekday() < 5]

        prices = []
        while business_days:
            on_date = business_days.pop(0)
            expiration_date = on_date - timedelta(days=1)

            close_price = get_eex_close_price(OPTION_ROOT, on_date, expiration_date, display_date)

            if not close_price:
                print(f"No data for {on_date}, skipping")
                continue

            prices.append(close_price)

        self.prices = prices

        len_prices = len(self.prices)
        self.status_message = f"Estimation based on all data ({len_prices}/{delta_days})"

        self.average_price = mean(self.prices)
        self.net_price = (self.average_price * STD_PROFILE_FACTOR + fees) / CONVERSION_FACTOR
        self.gross_price = self.net_price * TAXES


class GoGreenEnergyFlexFuture(GoGreenEnergyFlex):

    def __init__(self, display_date: date) -> None:
        super().__init__(display_date, fees=FUTURE_FEES)
