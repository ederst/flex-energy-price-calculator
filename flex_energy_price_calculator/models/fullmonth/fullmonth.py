from datetime import date, timedelta

from ..base import BaseModel
from ..registry import register


@register(
    "fullmonth",
    description="Full Month tariff (no fees)",
    fees=0.0,
    date_range_type="full_month",
    option_root="E.ATBM",
)
class FullMonth(BaseModel):

    def calculate_date_range(self, display_date: date):
        end_date = min(display_date - timedelta(days=1), date.today() - timedelta(days=1))
        start_date = date(end_date.year, end_date.month, 1)
        return start_date, end_date
