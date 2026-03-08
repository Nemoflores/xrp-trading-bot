import os
from binance.client import Client


class Executor:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.client = None

        if not self.dry_run:
            if not self.api_key or not self.api_secret:
                raise ValueError("Sätt BINANCE_API_KEY och BINANCE_API_SECRET i miljövariabler.")
            self.client = Client(self.api_key, self.api_secret)

    def open_position(self, symbol: str, side: str, quantity: float):
        if side not in ("BUY", "SELL"):
            raise ValueError("side måste vara BUY eller SELL.")
        if quantity <= 0:
            raise ValueError("quantity måste vara större än 0.")

        if self.dry_run:
            print("DRY RUN - order som skulle skickas:")
            print({
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": quantity
            })
            return {
                "dry_run": True,
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": quantity
            }

        return self.client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )

    def get_futures_usdt_balance(self):
        if self.dry_run:
            return 10000.0  # testvärde i dry run

        balances = self.client.futures_account_balance()
        for b in balances:
            if b["asset"] == "USDT":
                return float(b["balance"])

        raise ValueError("Hittade inget USDT-saldo.")

    def has_open_position(self, symbol: str):
        if self.dry_run:
            return False

        positions = self.client.futures_position_information(symbol=symbol)
        for p in positions:
            amt = float(p["positionAmt"])
            if amt != 0:
                return True
        return False