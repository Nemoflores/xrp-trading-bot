from binance.client import Client


class MarketData:
    def __init__(self):
        self.client = Client()

    def get_klines(
        self,
        symbol: str = "XRPUSDT",
        interval: str = Client.KLINE_INTERVAL_30MINUTE,
        limit: int = 300,
    ):
        return self.client.futures_klines(
            symbol=symbol,
            interval=interval,
            limit=limit
        )

    def get_ohlcv(
        self,
        symbol: str = "XRPUSDT",
        interval: str = Client.KLINE_INTERVAL_30MINUTE,
        limit: int = 300,
    ):
        klines = self.get_klines(symbol=symbol, interval=interval, limit=limit)

        return {
            "open": [float(k[1]) for k in klines],
            "high": [float(k[2]) for k in klines],
            "low": [float(k[3]) for k in klines],
            "close": [float(k[4]) for k in klines],
            "volume": [float(k[5]) for k in klines],
        }