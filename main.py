import time
from binance.client import Client
from market_data import MarketData
from strategy import DualModeStrategy
from risk_manager import RiskManager
from executor import Executor

SYMBOL = "XRPUSDT"
INTERVAL = Client.KLINE_INTERVAL_30MINUTE


def run_bot():
    md = MarketData()
    strategy = DualModeStrategy()
    executor = Executor(dry_run=True)

    # Tillfällig fast balans för test
    account_balance = executor.get_futures_usdt_balance()
    risk_manager = RiskManager(
        account_balance_usdt=account_balance,
        risk_per_trade_pct=1.0,
        max_notional_pct=20.0,
    )

    last_candle = None
    last_signal_side = None

    print("Bot startad...")
    print(f"Symbol: {SYMBOL}")
    print(f"Interval: {INTERVAL}")



    while True:
        try:
            klines = md.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=300)
            candle_time = klines[-1][0]

            if candle_time != last_candle:
                last_candle = candle_time

                ohlcv = md.get_ohlcv(symbol=SYMBOL, interval=INTERVAL, limit=300)

                signal = strategy.generate_signal(
                    highs=ohlcv["high"],
                    lows=ohlcv["low"],
                    closes=ohlcv["close"],
                    volumes=ohlcv["volume"]
                )

                print("\n==============================")
                print("Ny candle upptäckt")
                print("Signal:", signal.side)
                print("Mode:", signal.mode)
                print("Reason:", signal.reason)
                print("Price:", signal.last_price)
                print("ATR:", signal.atr)
                print("ADX:", signal.adx)
                print("RSI:", signal.rsi)

                if signal.side in ["BUY", "SELL"]:
                    if signal.side == last_signal_side:
                        print("Samma signal som sist, ingen ny order.")
                    else:
                        last_signal_side = signal.side

                        tp_distance = signal.atr * signal.tp_multiplier

                        plan = risk_manager.build_plan(
                            side=signal.side,
                            entry_price=signal.last_price,
                            stop_distance=signal.stop_distance,
                            tp_distance=tp_distance,
                        )

                        print("Riskplan:", plan)

                        result = executor.open_position(
                            symbol=SYMBOL,
                            side=signal.side,
                            quantity=plan.quantity
                        )

                        print("Orderresultat:", result)

                else:
                    print("Ingen trade denna candle.")

            time.sleep(20)

        except Exception as e:
            print("Fel uppstod:", e)
            time.sleep(20)


if __name__ == "__main__":
    run_bot()

