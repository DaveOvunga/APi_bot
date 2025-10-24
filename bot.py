import yfinance as yf
import pandas as pd
import numpy as np
import time
import requests

# Configuration Telegram
TELEGRAM_BOT_TOKEN = '8223573513:AAF56ggMmkO70d0QiJgz_FUxGUpqnl6_-YA'
TELEGRAM_CHAT_ID = '5892783171'  # Remplace par ton vrai Chat ID

def send_telegram_alert(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

def monitor_gold_market():
    already_alerted = set()

    while True:
        try:
            # Récupérer les données minute par minute
            gold = yf.Ticker("GC=F")
            data = gold.history(period="1d", interval="1m")

            # Nettoyer les données
            data = data.reset_index()
            data.dropna(inplace=True)

            # Calcul du pourcentage de variation
            data['Pct_Change'] = data['Close'].pct_change() * 100

            # Détection des impulsions
            data['Impulse'] = (data['Pct_Change'].abs() >= 1.0).astype(int)

            # Calcul du midpoint
            data['Midpoint'] = np.nan
            impulse_indices = data[data['Impulse'] == 1].index
            for idx in impulse_indices:
                high = data.loc[idx, 'High']
                low = data.loc[idx, 'Low']
                midpoint = (high + low) / 2
                data.loc[idx, 'Midpoint'] = midpoint

            # Vérifier et alerter
            for idx, row in data.iterrows():
                key = f"{row['Datetime']}_{row['Midpoint']:.2f}"
                if row['Impulse'] == 1 and row['Close'] <= row['Midpoint'] and key not in already_alerted:
                    alert_message = f"{row['Datetime']} → Impulsion détectée. Midpoint: {row['Midpoint']:.2f}, Prix actuel: {row['Close']:.2f}"
                    print(alert_message)
                    send_telegram_alert(alert_message)
                    already_alerted.add(key)

        except Exception as e:
            print(f"Erreur dans la boucle principale : {e}")

        time.sleep(60)  # Attendre 1 minute avant de relancer

# Lancer le bot
monitor_gold_market()
