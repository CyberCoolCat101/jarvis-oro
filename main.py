import os
import time
import requests
import google.generativeai as genai
from flask import Flask

# Configuración de Flask para que Render detecte el Web Service activo
app = Flask(__name__)

@app.route('/')
def home():
    return "Jarvis Gold Monitor 24/7 está activo y vigilando el oro, rey."

# Cargar credenciales desde las variables de entorno de Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

genai.configure(api_key=GEMINI_API_KEY)

def obtener_precio_oro():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=5m"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        meta = response['chart']['result'][0]['meta']
        return meta['regularMarketPrice']
    except Exception as e:
        print(f"Error obteniendo precio: {e}")
        return None

def analizar_con_jarvis(precio):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Eres Jarvis, un analista senior de trading cuantitativo en el Oro (XAU/USD).
        El precio actual es {precio}.
        Analiza si hay una oportunidad EXCEPCIONAL de compra o venta en este instante.
        REGLA: Solo responde 'Oportunidad' si la probabilidad de éxito es muy alta. Si no, responde 'Esperar'.
        Si hay oportunidad, responde exactamente en este formato:
        TIPO: [COMPRA/VENTA]
        ENTRADA: [Precio]
        STOP LOSS: [Precio]
        TAKE PROFIT: [Precio]
        MOTIVO: [Explicación en 1 frase]
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error con Gemini: {e}")
        return "Esperar"

def enviar_alerta_telegram(mensaje):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"👑 **ALERTA DE JARVIS - ORO** 👑\n\n{mensaje}",
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# Hilo en segundo plano para vigilar 24/7
import threading
def bucle_vigilancia():
    print("Iniciando bucle de vigilancia 24/7...")
    while True:
        precio = obtener_precio_oro()
        if precio:
            print(f"Precio actual del Oro: {precio}")
            analisis = analizar_con_jarvis(precio)
            if "TIPO:" in analisis:
                enviar_alerta_telegram(analisis)
                time.sleep(3600) # Esperar 1 hora si manda alerta
        time.sleep(300) # Revisar cada 5 minutos

if __name__ == '__main__':
    # Arrancar el vigilante en segundo plano
    t = threading.Thread(target=bucle_vigilancia)
    t.daemon = True
    t.start()
    
    # Iniciar servidor web Flask para Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)