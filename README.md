# ⚽ AI Sports Prediction Bot (Mundial 2026)

## 📌 Descripción del Proyecto
Este proyecto es un bot automatizado desarrollado en Python que genera pronósticos diarios para los partidos del Mundial de Fútbol. Utiliza la API de **Google Gemini (LLM)** para analizar los encuentros programados y sugerir marcadores basándose en estadística reciente e historial (H2H).

El diferenciador principal de este bot es su enfoque analítico de **optimización de reglas de negocio**: el prompt de la IA está configurado para explotar una oportunidad matemática en el reglamento del torneo, obligando a generar siempre predicciones de penales como cobertura de riesgo para maximizar la recolección de puntos.

## 🛠️ Stack Tecnológico y Arquitectura
* **Lenguaje:** Python 3.x
* **Inteligencia Artificial:** Google Gemini API (`google-genai`, modelo `gemini-2.5-flash`).
* **Notificaciones:** `smtplib` y `email.mime` (Protocolo SMTP para envío automatizado de correos).
* **Orquestación y CI/CD:** GitHub Actions (Cron Jobs para ejecución diaria sin necesidad de servidores locales).
* **Seguridad:** Gestión estricta de credenciales a través de variables de entorno (`os.environ`) y GitHub Secrets.

## ⚙️ Características Principales
1.  **Integración de IA Generativa:** Conexión directa con modelos fundacionales de Google para el procesamiento de lenguaje natural y análisis de datos deportivos.
2.  **Automatización Cloud-Native:** El script está diseñado para ejecutarse de forma autónoma en la nube todos los días a las 7:30 a.m. (UTC-5) mediante flujos de trabajo de GitHub Actions.
3.  **Seguridad de Grado de Producción:** El código fuente es público, pero la arquitectura garantiza la protección total de las API Keys y contraseñas de aplicación mediante inyección segura de dependencias.
4.  **Entrega de Resultados:** Formateo automático de la salida del LLM y envío directo a la bandeja de entrada del usuario final.

## 🚀 Cómo funciona el flujo (Pipeline)
1.  **Trigger:** GitHub Actions dispara el workflow según la programación definida.
2.  **Extracción de Datos:** El script se autentica de forma segura con la API de Gemini.
3.  **Procesamiento (LLM):** Se envía un prompt estructurado exigiendo el análisis de los partidos del día y la aplicación de la regla de cobertura de penales.
4.  **Notificación:** El resultado se empaqueta en un mensaje MIME y se distribuye vía correo electrónico utilizando un servidor SMTP seguro (TLS).
