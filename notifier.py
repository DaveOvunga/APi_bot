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
        self._send(message)

    def send_pre_spike_alert(self, info):
        message = (
            f"⚠️ *Pré-spike détecté !*\n"
            f"Symbole : {info['symbol']}\n"
            f"Type probable : {info['type']}\n"
            f"Prix actuel : {info['price']:.2f}\n"
            f"Tendance : {info['trend']}\n"
            f"Heure : {info['timestamp'].strftime('%H:%M:%S')}\n"
            f"_Prépare-toi à te positionner_"
        )
        self._send(message)

    def send_entry_confirmation(self, info):
        message = (
            f"✅ *Confirmation d’entrée recommandée*\n"
            f"Symbole : {info['symbol']}\n"
            f"Type : {info['type']}\n"
            f"Prix : {info['price']:.2f}\n"
            f"Tendance : {info['trend']}\n"
            f"Heure : {info['timestamp'].strftime('%H:%M:%S')}\n"
            f"_Tu peux te positionner maintenant_"
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
            requests.post(url, json=payload)
        except Exception as e:
            print(f"❌ Erreur Telegram : {e}")
