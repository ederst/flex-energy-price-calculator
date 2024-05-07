from datetime import date, timedelta
from statistics import mean

from ..base import CONVERSION_FACTOR, STD_PROFILE_FACTOR, TAXES, get_eex_close_price

DAYS = 10
FEES = 9.26

OPTION_ROOT = "E.ATBM"  # EX Phelix AT Future Monthly Base


class OekoFlow10:

    def __init__(self, display_date: date) -> None:
        # limit the end date to today
        end_date = min(
            display_date - timedelta(days=1),
            date.today() - timedelta(days=1),
        )
        start_date = date(end_date.year, end_date.month, 1)

        delta_days = (end_date - start_date).days
        all_days = [start_date + timedelta(days=x) for x in range(delta_days + 1)]

        # Note(sprietl):
        #  Calculate just the business days.
        #  Currently, this does not account for the bank holidays.
        business_days = [d for d in all_days if d.weekday() < 5]

        prices = []
        while len(prices) < DAYS and business_days:
            on_date = business_days.pop(0)
            expiration_date = on_date - timedelta(days=1)

            close_price = get_eex_close_price(OPTION_ROOT, on_date, expiration_date, display_date)

            if not close_price:
                print(f"No data for {on_date}, skipping")
                continue

            prices.append(close_price)

        self.prices = prices

        len_prices = len(self.prices)
        if len_prices == DAYS:
            self.status_message = f"Estimation based on all data ({len_prices}/{DAYS})"
        else:
            self.status_message = f"Estimation based on missing data ({len_prices}/{DAYS})"

        self.average_price = mean(self.prices)
        self.net_price = (self.average_price * STD_PROFILE_FACTOR + FEES) / CONVERSION_FACTOR
        self.gross_price = self.net_price * TAXES
