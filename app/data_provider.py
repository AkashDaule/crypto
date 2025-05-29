# app/data_provider.py

import requests
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

API_URL = "https://api.binance.com/api/v3/trades"

def fetch_price(symbol: str) -> Optional[Dict[str, float]]:
    try:
        response = requests.get(API_URL, params={"symbol": symbol, "limit": 50}, timeout=5)
        response.raise_for_status()
        trades: List[Dict] = response.json()

        if not trades:
            return None

        # Extract last trade price and total volume
        last_price = float(trades[-1]["price"])
        total_volume = sum(float(trade["qty"]) for trade in trades)

        return {
            "lastPrice": last_price,
            "volume": total_volume
        }
    except requests.RequestException as e:
        logger.error(f"API call failed: {e}")
        return None
