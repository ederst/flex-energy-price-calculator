from datetime import date, timedelta

from ..base import BaseModel
from ..registry import register


@register(
    "gogreenenergyflex",
    description="GoGreen Energy Flex tariff",
    fees=9.75,
    date_range_type="custom_range",
    option_root="E.ATBM",
    start_day=21,
    end_day=20,
)
class GoGreenEnergyFlex(BaseModel):

    def calculate_date_range(self, display_date: date):
        meta = type(self).__registry_metadata__
        end_date = min(
            (display_date - timedelta(days=1)).replace(day=meta.end_day),
            date.today() - timedelta(days=1),
        )
        start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=meta.start_day)
        return start_date, end_date


@register(
    "gogreenenergyflexfuture",
    description="GoGreen Energy Flex Future tariff",
    fees=14.75,
    date_range_type="custom_range",
    option_root="E.ATBM",
    start_day=21,
    end_day=20,
)
class GoGreenEnergyFlexFuture(BaseModel):

    def calculate_date_range(self, display_date: date):
        meta = type(self).__registry_metadata__
        end_date = min(
            (display_date - timedelta(days=1)).replace(day=meta.end_day),
            date.today() - timedelta(days=1),
        )
        start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=meta.start_day)
        return start_date, end_date
