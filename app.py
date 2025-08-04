import os
from flask import Flask, request, jsonify, send_file
from gtts import gTTS
import wikipedia
import io

app = Flask(__name__)

# Configuración básica para manejar CORS (crucial para apps móviles)
# Esto permite que tu app móvil, ejecutada desde otro origen, pueda acceder a tu API
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*' # O especifica tu dominio de app movil
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

# Endpoint de ejemplo para el estado del servidor
@app.route('/')
def home():
    return jsonify({"message": "API de Tabla Periódica en funcionamiento!"})

# Endpoint para síntesis de voz usando gTTS
@app.route('/speak', methods=['POST'])
def speak_text():
    data = request.json
    text = data.get('text')
    lang = data.get('lang', 'es') # Idioma por defecto español

    if not text:
        return jsonify({"error": "Se requiere el parámetro 'text'"}), 400

    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return send_file(mp3_fp, mimetype='audio/mpeg')
    except Exception as e:
        app.logger.error(f"Error en /speak: {e}")
        return jsonify({"error": f"Error al generar el audio: {str(e)}"}), 500

# Endpoint para buscar en Wikipedia
@app.route('/wiki_search', methods=['GET'])
def wiki_search():
    query = request.args.get('query')
    lang = request.args.get('lang', 'es') # Idioma por defecto español

    if not query:
        return jsonify({"error": "Se requiere el parámetro 'query'"}), 400

    try:
        wikipedia.set_lang(lang)
        summary = wikipedia.summary(query, sentences=2) # Obtiene un resumen de 2 frases
        return jsonify({"summary": summary})
    except wikipedia.exceptions.PageError:
        return jsonify({"error": "No se encontró la página de Wikipedia para esa consulta"}), 404
    except Exception as e:
        app.logger.error(f"Error en /wiki_search: {e}")
        return jsonify({"error": f"Error al buscar en Wikipedia: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000)) # Render asignará el puerto vía ENV
    app.run(host="0.0.0.0", port=port)
