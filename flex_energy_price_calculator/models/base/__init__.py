import json
import logging
import os
import time
from abc import ABC, abstractmethod
from datetime import date, timedelta
from functools import wraps
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Tuple

import requests

logger = logging.getLogger(__name__)

CONVERSION_FACTOR = 10
STD_PROFILE_FACTOR = 1.1
TAXES = 1.2

DEFAULT_URL = "https://api.eex-group.com/pub/market-data/chart/eod"
DEFAULT_CACHE_DIR = Path.cwd() / ".cache"

_OPTION_ROOT_PARAMS: dict[str, tuple[str, str, str, str, str]] = {
    'E.ATBM': ('ATBM', 'POWER', 'Future', 'AT', 'Base'),
}


def retry_on_auth_failure(max_retries: int = 3, initial_delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.HTTPError as e:
                    if e.response is not None and e.response.status_code in (401, 403):
                        if attempt < max_retries - 1:
                            time.sleep(delay)
                            delay *= 2
                        else:
                            raise
                    else:
                        raise

        return wrapper

    return decorator


@retry_on_auth_failure()
def get_eex_prices(option_root: str, display_date: date, start_date: date, end_date: date) -> Dict[str, Any]:
    short_code, commodity, pricing, area, product = _OPTION_ROOT_PARAMS[option_root]
    maturity = display_date.strftime('%Y%m')

    params = {
        'shortCode': short_code,
        'commodity': commodity,
        'pricing': pricing,
        'area': area,
        'product': product,
        'maturity': maturity,
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
    }

    cache_key = f"{option_root}_{maturity}_{start_date.isoformat()}_{end_date.isoformat()}.json"
    cache_file = Path(DEFAULT_CACHE_DIR) / cache_key

    if cache_file.exists():
        with open(cache_file, 'r') as f:
            return json.load(f)

    headers = {os.getenv("EEX_API_HEADER_KEY"): os.getenv("EEX_API_HEADER_VALUE")}
    logger.debug(
        f"Requesting EEX chart data: shortCode={short_code}, maturity={maturity}, start={start_date}, end={end_date}"
    )
    try:
        response = requests.get(DEFAULT_URL, params=params, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else "unknown"
        text = e.response.text[:200] if e.response else "no response"
        logger.error(f"EEX API request failed: {status} - {text}")
        raise

    prices = response.json()

    with open(cache_file, 'w') as f:
        f.write(response.text)

    return prices


def delete_cache_file(option_root: str, display_date: date, start_date: date, end_date: date) -> None:
    maturity = display_date.strftime('%Y%m')
    cache_key = f"{option_root}_{maturity}_{start_date.isoformat()}_{end_date.isoformat()}.json"
    cache_file = Path(DEFAULT_CACHE_DIR) / cache_key
    cache_file.unlink(missing_ok=True)


def _first_close_price(on_date: date, prices: Dict[str, Any]) -> float | None:
    on_date_str = on_date.isoformat()
    for series in prices.get('series', []):
        if series.get('serieName') == 'settlPx':
            for date_str, price in series.get('timeAndValue', []):
                if date_str == on_date_str:
                    return price
    return None


class BaseModel(ABC):
    @abstractmethod
    def calculate_date_range(self, display_date: date) -> Tuple[date, date]:
        """Return (start_date, end_date) for the calculation window."""
        pass

    def should_continue_loop(self, prices: List, business_days: List, meta: Any) -> bool:
        """Return True if loop should continue. Override for models with day limits."""
        return True

    def get_status_message(self, len_prices: int, delta_days: int) -> str:
        """Format status message. Override for custom formats."""
        return f"Estimation based on all data ({len_prices}/{delta_days})"

    def __init__(self, display_date: date) -> None:
        meta = type(self).__registry_metadata__

        start_date, end_date = self.calculate_date_range(display_date)

        delta_days = (end_date - start_date).days
        all_days = [start_date + timedelta(days=x) for x in range(delta_days + 1)]
        business_days = [d for d in all_days if d.weekday() < 5]

        raw_prices = get_eex_prices(meta.option_root, display_date, start_date, end_date)

        prices = []
        skipped_days = []
        while self.should_continue_loop(prices, business_days, meta) and business_days:
            on_date = business_days.pop(0)
            close_price = _first_close_price(on_date, raw_prices)

            if not close_price:
                skipped_days.append(on_date)
                continue

            prices.append((on_date, close_price))

        self.prices = prices
        self.skipped_days = skipped_days
        price_values = [x[1] for x in self.prices]

        if not price_values:
            self.average_price = 0.0
            self.net_price = 0.0
            self.gross_price = 0.0
            self.status_message = "No data available"
        else:
            self.status_message = self.get_status_message(len(price_values), delta_days)
            self.average_price = mean(price_values)
            self.net_price = (self.average_price * STD_PROFILE_FACTOR + meta.fees) / CONVERSION_FACTOR
            self.gross_price = self.net_price * TAXES
