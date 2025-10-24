import os
import requests

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_spike_alert(self, spike_info):
        message = (
            f"📊 *Spike détecté !*\n"
            f"Symbole : {spike_info['symbol']}\n"
            f"Type : {spike_info['type']}\n"
            f"Prix : {spike_info['price']:.2f}\n"
            f"Variation : {spike_info['variation_pct']:.2f}%\n"
            f"Tendance : {spike_info['trend']}\n"
            f"Heure : {spike_info['timestamp'].strftime('%H:%M:%S')}"
        )
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Erreur envoi Telegram : {e}")
