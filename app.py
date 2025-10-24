from flask import Flask
import threading
from bot import launch_bot

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot Deriv actif sur Render"

@app.route('/start')
def start_bot():
    threading.Thread(target=launch_bot).start()
    return "🚀 Bot lancé"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
