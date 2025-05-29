# tests/test_data_provider.py

from app.data_provider import fetch_price

def test_fetch_price():
    data = fetch_price("BTCUSDT")
    assert data is not None
    assert "lastPrice" in data
