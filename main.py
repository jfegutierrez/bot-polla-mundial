import os
import time
from datetime import datetime, timedelta
from google import genai
from google.genai import types
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. Configuración de credenciales de entorno
API_KEY = os.environ.get('GEMINI_API_KEY')
EMAIL_PASS = os.environ.get('GMAIL_PASS')
MI_CORREO = os.environ.get('MI_CORREO')
DESTINATARIOS = os.environ.get('DESTINATARIOS', MI_CORREO).split(',')

def generar_pronosticos():
    # Sincronización horaria (Ajuste para Zona Horaria de Colombia)
    hora_utc = datetime.utcnow()
    hoy_colombia = hora_utc - timedelta(hours=5)
    fecha_formateada = hoy_colombia.strftime('%d/%m/%Y')
    
    inicio_eliminatorias = datetime(2026, 6, 28)
    if hoy_colombia >= inicio_eliminatorias:
        regla_penales = "Fase de eliminación directa activa. Incluye obligatoriamente una columna indicando qué equipo clasifica en caso de empate y definición por penales."
    else:
        regla_penales = "Fase de Grupos activa. Los partidos pueden terminar en empate tras los 90 minutos reglamentarios. No habilites columnas de penales."

    # Prompt delegando la responsabilidad de buscar en internet
    prompt = f"""
    Eres un Analista de Datos experto en fútbol. Hoy es {fecha_formateada}.
    
    INSTRUCCIÓN PRINCIPAL (BÚSQUEDA WEB):
    Usa tu herramienta de Google Search para buscar y confirmar el fixture oficial de partidos de la Copa Mundial de la FIFA 2026 programados EXCLUSIVAMENTE para hoy: {fecha_formateada}.
    
    Si tu búsqueda en internet confirma que NO hay partidos oficiales del Mundial programados para hoy, devuelve ÚNICAMENTE este bloque HTML:
    <div style='text-align: center; padding: 30px; background: #fff3cd; color: #856404; border-radius: 8px; font-family: sans-serif;'><b>No hay partidos oficiales programados para el Mundial 2026 el día de hoy ({fecha_formateada}).</b></div>
    
    Si tu búsqueda en internet confirma que SÍ hay partidos hoy, analízalos y devuelve ÚNICAMENTE el código HTML de una tabla (sin markdown, sin ```html).
    - Usa estilos CSS en línea para garantizar un diseño premium: <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;">
    - Encabezados: <th style="background-color: #0A1A2F; color: #ffffff; padding: 14px; text-align: left;">
    - Celdas: <td style="padding: 14px; border-bottom: 1px solid #e2e8f0;">
    Columnas requeridas: Partido | Top 2 Marcadores (90 min) | Justificación Analítica (Enfoque estadístico).
    {regla_penales}
    """

    try:
        client = genai.Client(api_key=API_KEY)
        
        # 2. Activar la conexión a Internet (Google Search Grounding)
        herramienta_busqueda = types.Tool(
            google_search=types.GoogleSearch()
        )
        configuracion = types.GenerateContentConfig(
            tools=[herramienta_busqueda],
            temperature=0.7 # Temperatura ideal para combinar búsqueda web y análisis
        )
        
        # 3. Lógica de Reintentos Automáticos (Anti Error 505)
        max_intentos = 3
        for intento in range(max_intentos):
            try:
                respuesta = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=configuracion
                )
                
                # Limpiamos el texto por si la IA insiste en poner las comillas invertidas
                html_limpio = respuesta.text.replace('```html', '').replace('```', '').strip()
                return html_limpio, fecha_formateada
                
            except Exception as e:
                error_str = str(e).lower()
                # Si el error es por saturación del servidor de Google
                if any(codigo in error_str for codigo in ["505", "503", "429", "high demand"]):
                    if intento < max_intentos - 1: # Si aún nos quedan intentos
                        print(f"Servidor saturado (Intento {intento+1}/{max_intentos}). Esperando 15 segundos para reintentar...")
                        time.sleep(15) # Pausar la ejecución 15 segundos
                        continue
                
                # Si es un error diferente o se acabaron los intentos, forzamos la salida
                raise e
                
    except Exception as e:
        return f"<h3 style='color: #ef4444; font-family: sans-serif;'>Error en procesamiento de IA tras {max_intentos} intentos: {e}</h3>", fecha_formateada

def enviar_correo(contenido_html, fecha_consulta):
    try:
        msg = MIMEMultipart()
        msg['From'] = MI_CORREO
        msg['To'] = ", ".join(DESTINATARIOS)
        msg['Subject'] = f"🏆 Predicciones Analíticas - Mundial 2026 ({fecha_consulta})"
        
        cuerpo_correo = f"""
        <!DOCTYPE html>
        <html>
            <body style="font-family: 'Segoe UI', Helvetica, Arial, sans-serif; background-color: #f1f5f9; padding: 30px; margin: 0;">
                <div style="max-width: 850px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;">
                    
                    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); color: #ffffff; padding: 35px 30px; text-align: center; border-bottom: 4px solid #b91c1c;">
                        <h1 style="margin: 0; font-size: 26px; font-weight: 700; letter-spacing: 0.5px;">POLLA MUNDIALISTA 2026</h1>
                        <p style="margin: 6px 0 0 0; font-size: 14px; color: #93c5fd; font-weight: 400;">Modelado de Datos y Búsqueda Web en Tiempo Real</p>
                    </div>
                    
                    <div style="padding: 35px 30px;">
                        <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 15px; margin-bottom: 25px; border-radius: 0 8px 8px 0;">
                            <span style="color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase; display: block; margin-bottom: 2px;">Ventana de Análisis</span>
                            <span style="color: #1e293b; font-size: 15px; font-weight: 700;">Partidos oficiales del día: {fecha_consulta}</span>
                        </div>
                        
                        {contenido_html}
                    </div>
                    
                    <div style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                        <p style="margin: 0; font-size: 11px; color: #94a3b8; line-height: 1.5;">
                            🤖 Este reporte se generó combinando IA con búsqueda en Internet (Google Search).
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(cuerpo_correo, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MI_CORREO, EMAIL_PASS)
        server.sendmail(MI_CORREO, DESTINATARIOS, msg.as_string())
        server.quit()
        print(f"[{datetime.now()}] Reporte enviado exitosamente.")
    except Exception as e:
        print(f"Fallo al despachar correo electrónico: {e}")

if __name__ == '__main__':
    pronosticos_hoy, fecha_hoy = generar_pronosticos()
    enviar_correo(pronosticos_hoy, fecha_hoy)
