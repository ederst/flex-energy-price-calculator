import json
import os
from datetime import date
from pathlib import Path
from typing import Any, Dict

import requests

QUERY_DATE_FORMAT = "%Y/%m/%d"
CONVERSION_FACTOR = 10
STD_PROFILE_FACTOR = 1.1
TAXES = 1.2

# TODO(sprietl): maybe parameterise the chain (gv.*, close)
DEFAULT_URL = "https://webservice-eex.gvsi.com/query/json/getChain/gv.pricesymbol/gv.displaydate/close/"
DEFAULT_HEADERS = {os.getenv("EEX_API_HEADER_KEY"): os.getenv("EEX_API_HEADER_VALUE")}
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

    response = requests.get(DEFAULT_URL, params=params, headers=DEFAULT_HEADERS)
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
