from datetime import date, timedelta
from statistics import mean

from ..base import CONVERSION_FACTOR, STD_PROFILE_FACTOR, TAXES, get_eex_close_price
from ..registry import register


@register(
    "lmavg",
    description="Last Month Average tariff",
    fees=9.26,
    date_range_type="last_month",
    option_root="E.ATBM",
)
class LastMonthAvg:

    def __init__(self, display_date: date) -> None:
        meta = type(self).__registry_metadata__

        end_date = min(
            display_date - timedelta(days=1),
            date.today() - timedelta(days=1),
        )
        start_date = date(end_date.year, end_date.month, 1)

        delta_days = (end_date - start_date).days
        all_days = [start_date + timedelta(days=x) for x in range(delta_days + 1)]

        business_days = [d for d in all_days if d.weekday() < 5]

        prices = []
        skipped_days = []
        while business_days:
            on_date = business_days.pop(0)
            expiration_date = on_date - timedelta(days=1)

            close_price = get_eex_close_price(meta.option_root, on_date, expiration_date, display_date)

            if not close_price:
                skipped_days.append(on_date)
                continue

            prices.append((on_date, close_price))

        self.prices = prices
        self.skipped_days = skipped_days
        price_values = [x[1] for x in self.prices]

        len_prices = len(price_values)
        self.status_message = f"Estimation based on {len_prices} days"

        self.average_price = mean(price_values)
        self.net_price = (self.average_price * STD_PROFILE_FACTOR + meta.fees) / CONVERSION_FACTOR
        self.gross_price = self.net_price * TAXES
