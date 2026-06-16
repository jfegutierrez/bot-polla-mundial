import os
from datetime import datetime
from google import genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. Cargar las llaves y correos desde GitHub
API_KEY = os.environ.get('GEMINI_API_KEY')
EMAIL_PASS = os.environ.get('GMAIL_PASS')
MI_CORREO = os.environ.get('MI_CORREO')
DESTINATARIOS = os.environ.get('DESTINATARIOS', MI_CORREO).split(',')

def generar_pronosticos():
    try:
        client = genai.Client(api_key=API_KEY)
        
        # 2. Lógica de fechas para la Fase del Mundial
        hoy = datetime.now()
        inicio_eliminatorias = datetime(2026, 6, 28)
        
        if hoy > inicio_eliminatorias:
            regla_penales = "REGLA ESTRICTA: Como ya pasamos el 28 de junio (Fase Eliminatoria), SIEMPRE debes incluir tu predicción de quién gana en los penales."
        else:
            regla_penales = "REGLA ESTRICTA: Como estamos en Fase de Grupos (antes del 28 de junio), NO incluyas predicciones de penales."

        # 3. El Prompt Definitivo (Top 2 marcadores + Justificación Estadística)
        prompt = f"""
        Eres un Analista de Datos experto en fútbol. 
        Analiza los partidos del Mundial de Fútbol 2026 programados para HOY.
        
        INSTRUCCIONES DE ANÁLISIS:
        1. Evalúa el rendimiento previo de los equipos en lo que va de este mismo Mundial.
        2. Para cada partido, dame SIEMPRE los DOS (2) marcadores exactos con mayor probabilidad matemática/estadística para los 90 minutos.
        3. {regla_penales}
        
        FORMATO DE ENTREGA:
        Devuelve ÚNICAMENTE código HTML válido (sin markdown, sin ```html). 
        Crea una tabla con diseño moderno, fuente limpia (sans-serif) y bordes sutiles.
        Columnas requeridas: 
        - Partido
        - Top 2 Marcadores (90 min)
        - Penales
        - Justificación (Explica brevemente POR QUÉ estos marcadores son los más probables basándote en goles esperados, defensa, historial o necesidad de puntos).
        
        Si no hay partidos hoy, devuelve un HTML con un mensaje indicándolo.
        """
        
        respuesta = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        html_limpio = respuesta.text.replace('```html', '').replace('```', '').strip()
        return html_limpio
        
    except Exception as e:
        return f"<h3>Error al generar pronósticos: {e}</h3>"

def enviar_correo(contenido_html):
    try:
        msg = MIMEMultipart()
        msg['From'] = MI_CORREO
        msg['To'] = ", ".join(DESTINATARIOS)
        msg['Subject'] = "⚽ Tus Pronósticos Diarios - Polla Mundialista 2026"
        
        mensaje_base = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>¡Hola! Aquí están los pronósticos de hoy:</h2>
                {contenido_html}
                <br><br>
                <p style="font-size: 12px; color: gray;"><i>Este correo fue generado automáticamente por un bot de Python con Inteligencia Artificial.</i></p>
            </body>
        </html>
        """
        msg.attach(MIMEText(mensaje_base, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MI_CORREO, EMAIL_PASS)
        server.sendmail(MI_CORREO, DESTINATARIOS, msg.as_string())
        server.quit()
        print(f"Correo enviado correctamente a {len(DESTINATARIOS)} destinatarios.")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

if __name__ == '__main__':
    pronosticos_hoy = generar_pronosticos()
    enviar_correo(pronosticos_hoy)
