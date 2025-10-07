# worker.py

# --- Importações Essenciais ---
from flask import Flask, request, send_file
from PIL import Image, ImageFilter
import io
import sys

# --- Inicialização da Aplicação Flask ---
app = Flask(__name__)

# --- Rota de Processamento ---
@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return "Erro: Nenhuma imagem enviada.", 400

    file = request.files['image']
    filter_type = request.form.get('filter', 'BLUR').upper()

    image = Image.open(file.stream)
    
    processed_image = None
    if filter_type == 'BLUR':
        processed_image = image.filter(ImageFilter.BLUR)
    elif filter_type == 'GRAYSCALE':
        processed_image = image.convert('L')
    elif filter_type == 'CONTOUR':
        processed_image = image.filter(ImageFilter.CONTOUR)
    else:
        processed_image = image

    byte_arr = io.BytesIO()
    processed_image.save(byte_arr, format='PNG')
    byte_arr.seek(0)

    return send_file(byte_arr, mimetype='image/png')

# --- Execução do Worker ---
if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    app.run(host='0.0.0.0', port=port)