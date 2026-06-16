import os
from datetime import datetime, timedelta
from google import genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. Configuración de credenciales de entorno
API_KEY = os.environ.get('GEMINI_API_KEY')
EMAIL_PASS = os.environ.get('GMAIL_PASS')
MI_CORREO = os.environ.get('MI_CORREO')
DESTINATARIOS = os.environ.get('DESTINATARIOS', MI_CORREO).split(',')

def generar_pronosticos():
    try:
        client = genai.Client(api_key=API_KEY)
        
        # Sincronización horaria (Ajuste para Zona Horaria de Colombia)
        hora_utc = datetime.utcnow()
        hoy_colombia = hora_utc - timedelta(hours=5)
        fecha_formateada = hoy_colombia.strftime('%d/%m/%Y')
        
        # =========================================================================
        # FIXTURE OFICIAL COMPLETO - FASE DE GRUPOS MUNDIAL FIFA 2026
        # =========================================================================
        calendario_mundial = {
            "11/06/2026": "Grupo A: México vs. Sudáfrica | Grupo A: Corea del Sur vs. República Checa",
            "12/06/2026": "Grupo B: Canadá vs. Bosnia y Herzegovina | Grupo D: Estados Unidos vs. Paraguay",
            "13/06/2026": "Grupo B: Catar vs. Suiza | Grupo C: Brasil vs. Marruecos | Grupo C: Haití vs. Escocia | Grupo D: Australia vs. Turquía",
            "14/06/2026": "Grupo E: Alemania vs. Curazao | Grupo F: Países Bajos vs. Japón | Grupo E: Costa de Marfil vs. Ecuador | Grupo F: Suecia vs. Túnez",
            "15/06/2026": "Grupo H: España vs. Cabo Verde | Grupo G: Bélgica vs. Egipto | Grupo H: Arabia Saudita vs. Uruguay | Grupo G: Irán vs. Nueva Zelanda",
            "16/06/2026": "Grupo I: Francia vs. Senegal | Grupo I: Irak vs. Noruega | Grupo J: Argentina vs. Algeria | Grupo J: Austria vs. Jordania",
            "17/06/2026": "Grupo K: Portugal vs. RD Congo | Grupo L: Inglaterra vs. Croacia | Grupo L: Ghana vs. Panamá | Grupo K: Uzbekistán vs. Colombia",
            "18/06/2026": "Grupo A: República Checa vs. Sudáfrica | Grupo B: Suiza vs. Bosnia y Herzegovina | Grupo B: Canadá vs. Catar | Grupo A: México vs. Corea del Sur",
            "19/06/2026": "Grupo C: Marruecos vs. Escocia | Grupo D: Estados Unidos vs. Australia | Grupo C: Brasil vs. Haití | Grupo D: Turquía vs. Paraguay",
            "20/06/2026": "Grupo E: Ecuador vs. Curazao | Grupo F: Japón vs. Túnez | Grupo E: Alemania vs. Costa de Marfil | Grupo F: Países Bajos vs. Suecia",
            "21/06/2026": "Grupo H: España vs. Arabia Saudita | Grupo G: Bélgica vs. Irán | Grupo H: Uruguay vs. Cabo Verde | Grupo G: Nueva Zelanda vs. Egipto",
            "22/06/2026": "Grupo I: Francia vs. Irak | Grupo J: Argentina vs. Austria | Grupo I: Noruega vs. Senegal | Grupo J: Jordania vs. Algeria",
            "23/06/2026": "Grupo K: Portugal vs. Uzbekistán | Grupo L: Inglaterra vs. Ghana | Grupo L: Panamá vs. Croacia | Grupo K: Colombia vs. RD Congo",
            "24/06/2026": "Grupo A: República Checa vs. México | Grupo A: Sudáfrica vs. Corea del Sur | Grupo B: Suiza vs. Canadá | Grupo B: Bosnia y Herzegovina vs. Catar",
            "25/06/2026": "Grupo C: Marruecos vs. Brasil | Grupo C: Escocia vs. Haití | Grupo D: Turquía vs. Estados Unidos | Grupo D: Paraguay vs. Australia",
            "26/06/2026": "Grupo E: Ecuador vs. Alemania | Grupo E: Curazao vs. Costa de Marfil | Grupo F: Japón vs. Países Bajos | Grupo F: Túnez vs. Suecia",
            "27/06/2026": "Grupo H: Uruguay vs. España | Grupo H: Cabo Verde vs. Arabia Saudita | Grupo G: Nueva Zelanda vs. Bélgica | Grupo G: Egipto vs. Irán | Grupo I: Noruega vs. Francia | Grupo I: Senegal vs. Irak | Grupo J: Jordania vs. Argentina | Grupo J: Algeria vs. Austria | Grupo K: Colombia vs. Portugal | Grupo K: RD Congo vs. Uzbekistán | Grupo L: Panamá vs. Inglaterra | Grupo L: Croacia vs. Ghana"
        }
        
        # Extraer partidos correspondientes al día de hoy
        partidos_de_hoy = calendario_mundial.get(fecha_formateada, "No hay partidos programados")
        
        # Si la fecha no se encuentra en el diccionario (ej. días de descanso pre-16avos o post-torneo)
        if partidos_de_hoy == "No hay partidos programados":
            return f"<div style='text-align: center; padding: 30px; background: #fff3cd; color: #856404; border-radius: 8px; font-family: sans-serif;'><b>No hay partidos oficiales programados para el Mundial 2026 el día de hoy ({fecha_formateada}).</b></div>", fecha_formateada

        # Control Dinámico de Fases (Grupos vs Eliminación Directa)
        inicio_eliminatorias = datetime(2026, 6, 28)
        if hoy_colombia >= inicio_eliminatorias:
            regla_penales = "Fase de eliminación directa activa. Incluye obligatoriamente una columna indicando qué equipo clasifica en caso de empate y definición por penales."
        else:
            regla_penales = "Fase de Grupos activa. Los partidos pueden terminar en empate tras los 90 minutos reglamentarios. No habilites columnas de penales."

        # 2. Prompt Estratégico con Inyección de Contexto Real y Estilos Embebidos
        prompt = f"""
        Eres un Analista de Datos experto en fútbol y modelos predictivos deportivos. Hoy es {fecha_formateada}.
        
        Tu tarea es generar el reporte de pronósticos EXCLUSIVAMENTE para los siguientes partidos del Mundial 2026:
        {partidos_de_hoy}
        
        REGLA ESTRICTA DE CONTEXTO:
        Bajo ninguna circunstancia asumas o inventes partidos de otros mundiales o de fechas distintas a hoy.
        
        INSTRUCCIONES DE ANÁLISIS:
        1. Evalúa el rendimiento de los equipos, nóminas, e historial táctico bajo un enfoque probabilístico.
        2. Proporciona los DOS (2) marcadores exactos más probables para el tiempo regular de cada partido.
        3. {regla_penales}
        
        FORMATO DE ENTREGA (CÓDIGO HTML PURO):
        Devuelve ÚNICAMENTE el código HTML de la tabla, sin bloques de código markdown (no uses ```html ni ```).
        Aplica de forma estricta los siguientes estilos CSS en línea para garantizar un diseño corporativo premium:
        - Estilo de tabla: <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-family: Arial, sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        - Encabezados: <th style="background-color: #0A1A2F; color: #ffffff; padding: 14px; text-align: left; font-size: 13px; text-transform: uppercase; border: 1px solid #112240;">
        - Celdas de datos: <td style="padding: 14px; border-bottom: 1px solid #e2e8f0; color: #334155; font-size: 14px; vertical-align: top;">
        - Alternancia de filas (opcional): usa un fondo sutil #F8FAFC para las filas pares si lo requieres.
        
        Columnas requeridas: Partido | Top 2 Marcadores (90 min) | Justificación Analítica (Enfoque breve basado en volumen de ataque y solidez defensiva esperada).
        """
        
        respuesta = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        # Limpieza de empaquetado del texto de respuesta
        html_limpio = respuesta.text.replace('```html', '').replace('```', '').strip()
        return html_limpio, fecha_formateada
        
    except Exception as e:
        return f"<h3 style='color: #ef4444;'>Error en procesamiento interno: {e}</h3>", datetime.now().strftime('%d/%m/%Y')

def enviar_correo(contenido_html, fecha_consulta):
    try:
        msg = MIMEMultipart()
        msg['From'] = MI_CORREO
        msg['To'] = ", ".join(DESTINATARIOS)
        msg['Subject'] = f"🏆 Predicciones Analíticas - Mundial 2026 ({fecha_consulta})"
        
        # 3. Contenedor HTML Estilo "Reporte de Inteligencia Deportiva"
        cuerpo_correo = f"""
        <!DOCTYPE html>
        <html>
            <body style="font-family: 'Segoe UI', Helvetica, Arial, sans-serif; background-color: #f1f5f9; padding: 30px; margin: 0;">
                <div style="max-width: 850px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;">
                    
                    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); color: #ffffff; padding: 35px 30px; text-align: center; border-bottom: 4px solid #b91c1c;">
                        <h1 style="margin: 0; font-size: 26px; font-weight: 700; letter-spacing: 0.5px;">POLA MUNDIALISTA 2026</h1>
                        <p style="margin: 6px 0 0 0; font-size: 14px; color: #93c5fd; font-weight: 400;">Modelado de Datos y Probabilidades Estatísticas</p>
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
                            Aviso: Este es un análisis automatizado optimizado por IA. Los datos del fixture corresponden a la programación oficial de la Copa Mundial de la FIFA 2026.
                        </p>
                    </div>

                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(cuerpo_correo, 'html'))

        # Configuración del canal de transporte SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MI_CORREO, EMAIL_PASS)
        server.sendmail(MI_CORREO, DESTINATARIOS, msg.as_string())
        server.quit()
        print(f"[{datetime.now()}] Reporte enviado exitosamente a los destinatarios.")
    except Exception as e:
        print(f"❌ Fallo crítico al despachar correo electrónico: {e}")

if __name__ == '__main__':
    pronosticos_hoy, fecha_hoy = generar_pronosticos()
    enviar_correo(pronosticos_hoy, fecha_hoy)
