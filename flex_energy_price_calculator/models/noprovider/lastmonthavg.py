from datetime import date, timedelta

from ..base import BaseModel
from ..registry import register


@register(
    "lmavg",
    description="Last Month Average tariff",
    fees=9.26,
    date_range_type="last_month",
    option_root="E.ATBM",
)
class LastMonthAvg(BaseModel):

    def calculate_date_range(self, display_date: date):
        end_date = min(display_date - timedelta(days=1), date.today() - timedelta(days=1))
        start_date = date(end_date.year, end_date.month, 1)
        return start_date, end_date

    def get_status_message(self, len_prices, delta_days):
        return f"Estimation based on {len_prices} days"
