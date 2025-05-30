import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

API_URL = "https://api.binance.com/api/v3/ticker/24hr"

def fetch_price(symbol: str) -> Optional[Dict]:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        response = requests.get(API_URL, params={"symbol": symbol}, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API call failed: {e}")
        return None
