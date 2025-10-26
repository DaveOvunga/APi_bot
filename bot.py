import websocket
import json
import threading
from datetime import datetime
import statistics
from notifier import TelegramNotifier

notifier = TelegramNotifier()
last_sent_trend = {}

SYMBOLS = {
    "Boom 1000": "BOOM1000",
    "Crash 1000": "CRASH1000",
    "Boom 500": "BOOM500",
    "Crash 500": "CRASH500"
}

APP_ID = "1089"

# === INDICATEURS TECHNIQUES ===

def calculate_ema(prices, period):
    if len(prices) < period:
        return None
    ema = prices[0]
    multiplier = 2 / (period + 1)
    for price in prices[1:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, period + 1):
        diff = prices[-i] - prices[-i - 1]
        if diff >= 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))
    if not gains and not losses:
        return 50
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_volatility(prices, period=20):
    if len(prices) < period:
        return None
    return statistics.stdev(prices[-period:])

# === LOGIQUE DU BOT ===

def confirm_entry(symbol_name, price, trend, timestamp, rsi):
    if trend in ["haussière", "baissière"]:
        if last_sent_trend.get(symbol_name) == trend:
            return  # Évite doublons
        last_sent_trend[symbol_name] = trend

        print(f"[SIGNAL] {symbol_name} | {trend.upper()} détectée à {price:.2f}")
        entry_info = {
            'symbol': symbol_name,
            'type': 'achat' if trend == 'haussière' else 'vente',
            'price': price,
            'timestamp': timestamp,
            'trend': trend,
            'rsi': rsi
        }
        notifier.send_entry_confirmation(entry_info)

def start_stream(symbol_name, symbol_code):
    previous_prices = []

    def on_message(ws, message):
        data = json.loads(message)
        if "tick" in data:
            price = float(data["tick"]["quote"])
            timestamp = datetime.fromtimestamp(data["tick"]["epoch"])
            previous_prices.append(price)

            if len(previous_prices) > 200:
                previous_prices.pop(0)

            ema_fast = calculate_ema(previous_prices, 5)
            ema_slow = calculate_ema(previous_prices, 15)
            rsi = calculate_rsi(previous_prices, 14)
            vol = calculate_volatility(previous_prices, 20)

            if not ema_fast or not ema_slow or not rsi or not vol:
                return

            # Conditions de spike probable :
            if ema_fast > ema_slow and rsi < 30:
                trend = "haussière"  # Boom spike imminent
            elif ema_fast < ema_slow and rsi > 70:
                trend = "baissière"  # Crash spike imminent
            else:
                trend = "neutre"

            if trend != "neutre":
                confirm_entry(symbol_name, price, trend, timestamp, rsi)

            print(f"[{symbol_name}] {timestamp.strftime('%H:%M:%S')} → {price:.2f} | RSI={rsi:.1f} | {trend}")

    def on_open(ws):
        print(f"🔗 Connexion WebSocket ouverte pour {symbol_name}")
        ws.send(json.dumps({
            "ticks": symbol_code,
            "subscribe": 1
        }))

    def on_error(ws, error):
        print(f"❌ Erreur WebSocket ({symbol_name}) : {error}")

    def on_close(ws, close_status_code, close_msg):
        print(f"🔌 Connexion WebSocket fermée ({symbol_name})")

    ws = websocket.WebSocketApp(
        f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

def launch_bot():
    for name, code in SYMBOLS.items():
        threading.Thread(target=start_stream, args=(name, code)).start()
