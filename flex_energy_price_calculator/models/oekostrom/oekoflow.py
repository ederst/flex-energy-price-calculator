from datetime import date, timedelta

from ..base import BaseModel
from ..registry import register


@register(
    "oekoflow1.0",
    description="OekoFlow 1.0 tariff",
    fees=9.26,
    date_range_type="full_month",
    option_root="E.ATBM",
    days=10,
)
class OekoFlow10(BaseModel):

    def calculate_date_range(self, display_date: date):
        end_date = min(display_date - timedelta(days=1), date.today() - timedelta(days=1))
        start_date = date(end_date.year, end_date.month, 1)
        return start_date, end_date

    def should_continue_loop(self, prices, business_days, meta):
        return len(prices) < meta.days

    def get_status_message(self, len_prices, delta_days):
        meta = type(self).__registry_metadata__
        if len_prices == meta.days:
            return f"Estimation based on all data ({len_prices}/{meta.days})"
        return f"Estimation based on missing data ({len_prices}/{meta.days})"
