import os
from dotenv import load_dotenv
import requests

# Charger les variables d’environnement (.env)
load_dotenv()

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_entry_confirmation(self, info):
        # Formatage du RSI
        rsi = info.get('rsi')
        rsi_text = f"{rsi:.1f}" if rsi is not None else "N/A"

        message = (
            f"🚨 *ALERTE SPIKE IMMINENT*\n\n"
            f"📊 Symbole : {info['symbol']}\n"
            f"🧭 Type : {info['type']}\n"
            f"💰 Prix : {info['price']:.2f}\n"
            f"📈 Tendance : {info['trend']}\n"
            f"📊 RSI : {rsi_text}\n"
            f"⏰ Heure : {info['timestamp'].strftime('%H:%M:%S')}\n\n"
            f"_Signal détecté par le bot Boom/Crash – stratégie EMA + RSI + Volatilité_"
        )

        self._send(message)

    def _send(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"⚠️ Erreur Telegram ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"❌ Erreur Telegram : {e}")
