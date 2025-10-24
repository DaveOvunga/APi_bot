import websocket
import json
import threading
import time
from datetime import datetime

notifier = TelegramNotifier()

SYMBOLS = {
    "Boom 1000": "R_100",
    "Crash 1000": "R_10",
    "Boom 500": "BOOM500",
    "Crash 500": "CRASH500"
}

SPIKE_THRESHOLD = 1.0  # % variation EMA
PIP_THRESHOLD = 50     # variation brute
APP_ID = "1089"

def start_stream(symbol_name, symbol_code):
    previous_prices = []

    def calculate_ema(prices, period):
        if len(prices) < period:
            return None
        weights = [2 / (period + 1)] * period
        ema = prices[-period]
        for i in range(-period + 1, 0):
            ema = (prices[i] - ema) * weights[0] + ema
        return ema

    def on_message(ws, message):
        data = json.loads(message)
        if "tick" in data:
            price = float(data["tick"]["quote"])
            timestamp = datetime.fromtimestamp(data["tick"]["epoch"])
            previous_prices.append(price)

            # EMA rapide et lente
            ema_fast = calculate_ema(previous_prices, 5)
            ema_slow = calculate_ema(previous_prices, 15)

            # Détection de tendance
            if ema_fast and ema_slow:
                if ema_fast > ema_slow:
                    trend = "haussière"
                elif ema_fast < ema_slow:
                    trend = "baissière"
                else:
                    trend = "neutre"
            else:
                trend = "indéterminée"

            # Spike par variation EMA
            if len(previous_prices) >= 10:
                ema = sum(previous_prices[-10:]) / 10
                variation_pct = ((price - ema) / ema) * 100

                if abs(variation_pct) >= SPIKE_THRESHOLD:
                    spike_info = {
                        'symbol': symbol_name,
                        'type': 'haussier' if variation_pct > 0 else 'baissier',
                        'price': price,
                        'previous_price': ema,
                        'variation_pct': variation_pct,
                        'timestamp': timestamp,
                        'trend': trend
                    }
                    notifier.send_spike_alert(spike_info)

            # Spike par variation brute
            if len(previous_prices) >= 2:
                last_price = previous_prices[-2]
                pip_diff = abs(price - last_price)

                if pip_diff >= PIP_THRESHOLD:
                    spike_info = {
                        'symbol': symbol_name,
                        'type': 'haussier' if price > last_price else 'baissier',
                        'price': price,
                        'previous_price': last_price,
                        'variation_pct': ((price - last_price) / last_price) * 100,
                        'timestamp': timestamp,
                        'trend': trend
                    }
                    notifier.send_spike_alert(spike_info)

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

# Lancer tous les flux en parallèle
for name, code in SYMBOLS.items():
    threading.Thread(target=start_stream, args=(name, code)).start()
    

def launch_bot():
    for name, code in SYMBOLS.items():
        threading.Thread(target=start_stream, args=(name, code)).start()

