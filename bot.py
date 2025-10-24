import websocket
import json
import threading
from datetime import datetime
from notifier import TelegramNotifier

notifier = TelegramNotifier()

SYMBOLS = {
    "Boom 1000": "R_100",
    "Crash 1000": "R_10",
    "Boom 500": "BOOM500",
    "Crash 500": "CRASH500"
}

APP_ID = "1089"

def calculate_ema(prices, period):
    if len(prices) < period:
        return None
    weights = [2 / (period + 1)] * period
    ema = prices[-period]
    for i in range(-period + 1, 0):
        ema = (prices[i] - ema) * weights[0] + ema
    return ema

def confirm_entry(symbol_name, price, trend, timestamp):
    if trend in ["haussière", "baissière"]:
        entry_info = {
            'symbol': symbol_name,
            'type': 'achat' if trend == 'haussière' else 'vente',
            'price': price,
            'timestamp': timestamp,
            'trend': trend
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

            ema_fast = calculate_ema(previous_prices, 5)
            ema_slow = calculate_ema(previous_prices, 15)

            if ema_fast and ema_slow:
                trend = "haussière" if ema_fast > ema_slow else "baissière" if ema_fast < ema_slow else "neutre"
            else:
                trend = "indéterminée"

            confirm_entry(symbol_name, price, trend, timestamp)

            print(f"[{symbol_name}] {timestamp.strftime('%H:%M:%S')} → {price:.2f} | Tendance : {trend}")

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
