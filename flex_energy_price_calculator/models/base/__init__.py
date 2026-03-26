import json
import os
from abc import ABC, abstractmethod
from datetime import date, timedelta
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Tuple

import requests

QUERY_DATE_FORMAT = "%Y/%m/%d"
CONVERSION_FACTOR = 10
STD_PROFILE_FACTOR = 1.1
TAXES = 1.2

# TODO(sprietl): maybe parameterise the chain (gv.*, close)
DEFAULT_URL = "https://webservice-eex.gvsi.com/query/json/getChain/gv.pricesymbol/gv.displaydate/close/"
DEFAULT_CACHE_DIR = Path.cwd() / ".cache"


def get_eex_prices(option_root: str, on_date: date, expiration_date: date) -> Dict[str, Any]:
    # Note(sprietl): For E.ATBM/ATPM we need these params:
    #   optionroot: "/E.ATBM"
    #   onDate: 2024/04/12
    #   expirationdate: 2024/04/11 (onDate - 1)
    params = {
        'optionroot': f"\"/{option_root}\"",
    }
    params['onDate'] = on_date.strftime(QUERY_DATE_FORMAT)
    params['expirationdate'] = expiration_date.strftime(QUERY_DATE_FORMAT)

    cache_file = Path(DEFAULT_CACHE_DIR) / f"{option_root}_{on_date.isoformat()}_{expiration_date.isoformat()}.json"

    if cache_file.exists():
        with open(cache_file, 'r') as f:
            return json.load(f)

    headers = {os.getenv("EEX_API_HEADER_KEY"): os.getenv("EEX_API_HEADER_VALUE")}
    response = requests.get(DEFAULT_URL, params=params, headers=headers)
    response.raise_for_status()

    prices = response.json()

    # if prices['results']['items']:
    with open(cache_file, 'w') as f:
        f.write(response.text)

    return prices


def delete_cache_file(option_root: str, on_date: date, expiration_date: date) -> None:
    cache_file = Path(DEFAULT_CACHE_DIR) / f"{option_root}_{on_date.isoformat()}_{expiration_date.isoformat()}.json"
    cache_file.unlink(missing_ok=True)


def _first_close_price(display_date: date, prices: Dict[str, Any]) -> str:
    display_date_str = display_date.strftime("%-m/%-d/%Y")
    for item in prices['results']['items']:
        if display_date_str != item['gv.displaydate']:
            continue

        return item['close']

    return None


def get_eex_close_price(option_root: str, on_date: date, expiration_date: date, display_date: date) -> str:

    prices = get_eex_prices(option_root, on_date, expiration_date)

    close_price = _first_close_price(display_date, prices)

    # if not close_price:
    #     # no data, we need no cache
    #     delete_cache_file(option_root, on_date, expiration_date)

    return close_price


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

        prices = []
        skipped_days = []
        while self.should_continue_loop(prices, business_days, meta) and business_days:
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

        self.status_message = self.get_status_message(len(price_values), delta_days)
        self.average_price = mean(price_values)
        self.net_price = (self.average_price * STD_PROFILE_FACTOR + meta.fees) / CONVERSION_FACTOR
        self.gross_price = self.net_price * TAXES
