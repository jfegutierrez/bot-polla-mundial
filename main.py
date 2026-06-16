import os
from datetime import datetime, timedelta
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
        
        hora_utc = datetime.utcnow()
        hoy_colombia = hora_utc - timedelta(hours=5)
        fecha_formateada = hoy_colombia.strftime('%d/%m/%Y')
        inicio_eliminatorias = datetime(2026, 6, 28)
        
        if hoy_colombia > inicio_eliminatorias:
            regla_penales = "Como ya pasamos el 28 de junio, SIEMPRE incluye una columna con tu predicción de quién gana en los penales."
        else:
            regla_penales = "Como estamos en Fase de Grupos, NO incluyas columna de predicciones de penales."

        # 2. Prompt con Candado Anti-Alucinaciones y Diseño Premium
        prompt = f"""
        Eres un Analista de Datos experto en fútbol. 
        Analiza los partidos del Mundial de Fútbol 2026 programados EXCLUSIVAMENTE para la fecha de hoy: {fecha_formateada}.
        
        REGLA ESTRICTA ANTI-ALUCINACIONES:
        Bajo ninguna circunstancia incluyas partidos, equipos o datos del Mundial de Qatar 2022. Si no hay partidos oficiales programados para el Mundial 2026 hoy {fecha_formateada}, devuelve ÚNICAMENTE esta frase exacta:
        "<div style='text-align: center; padding: 30px; background: #fff3cd; color: #856404; border-radius: 8px;'><b>No hay partidos programados para el Mundial 2026 el día de hoy ({fecha_formateada}).</b></div>"
        
        INSTRUCCIONES DE ANÁLISIS (Solo si hay partidos hoy):
        1. Evalúa el rendimiento previo de los equipos en este mismo Mundial.
        2. Dame los DOS (2) marcadores exactos con mayor probabilidad matemática para los 90 minutos.
        3. {regla_penales}
        
        FORMATO DE ENTREGA (DISEÑO PREMIUM):
        Devuelve ÚNICAMENTE código HTML válido. No uses markdown.
        Construye una tabla con estilos CSS integrados:
        - Etiqueta <table> con ancho del 100% y border-collapse: collapse.
        - Etiqueta <th> (encabezados) con fondo color #0A1A2F (azul muy oscuro), texto #FFFFFF, padding de 12px y texto centrado.
        - Etiqueta <td> con padding de 12px, borde inferior de 1px solid #DDDDDD, texto color #333333.
        Las columnas deben ser: Partido | Top 2 Marcadores (90 min) | Penales (si aplica) | Justificación (corta y analítica).
        """
        
        respuesta = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        html_limpio = respuesta.text.replace('```html', '').replace('```', '').strip()
        return html_limpio, fecha_formateada
        
    except Exception as e:
        return f"<h3>Error al generar pronósticos: {e}</h3>", datetime.now().strftime('%d/%m/%Y')

def enviar_correo(contenido_html, fecha_consulta):
    try:
        msg = MIMEMultipart()
        msg['From'] = MI_CORREO
        msg['To'] = ", ".join(DESTINATARIOS)
        msg['Subject'] = f"🏆 Reporte Analítico - Polla Mundialista 2026 ({fecha_consulta})"
        
        # 3. Plantilla de correo estilo "Reporte Ejecutivo"
        mensaje_base = f"""
        <!DOCTYPE html>
        <html>
            <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f7f6; padding: 20px; margin: 0;">
                <div style="max-width: 800px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                    
                    <div style="background-color: #C2002F; color: #ffffff; padding: 25px; text-align: center;">
                        <h2 style="margin: 0; font-size: 24px; letter-spacing: 1px;">Pronósticos Mundial 2026</h2>
                        <p style="margin: 8px 0 0 0; font-size: 14px; opacity: 0.9;">Reporte Estadístico Diario</p>
                    </div>
                    
                    <div style="padding: 30px;">
                        <p style="color: #555555; font-size: 14px; margin-bottom: 20px;">
                            <b>Fecha de análisis:</b> {fecha_consulta} (Hora Colombia)
                        </p>
                        {contenido_html}
                    </div>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; text-align: center; border-top: 1px solid #eeeeee;">
                        <p style="margin: 0; font-size: 11px; color: #888888;">
                            🤖 Este es un reporte automatizado generado por Inteligencia Artificial y Python.
                        </p>
                    </div>

                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(mensaje_base, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MI_CORREO, EMAIL_PASS)
        server.sendmail(MI_CORREO, DESTINATARIOS, msg.as_string())
        server.quit()
        print("Correo enviado correctamente.")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

if __name__ == '__main__':
    pronosticos_hoy, fecha_hoy = generar_pronosticos()
    enviar_correo(pronosticos_hoy, fecha_hoy)
