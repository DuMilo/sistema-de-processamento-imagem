# server.py

# --- Importações Essenciais ---
from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import random

# --- Configuração Inicial ---
app = Flask(__name__)
UPLOAD_FOLDER = 'processed_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

WORKER_URLS = [
    "http://127.0.0.1:5001/process",
    "http://127.0.0.1:5002/process",
]

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Rota de Upload e Distribuição ---
@app.route('/upload', methods=['POST'])
def upload_and_distribute():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada."}), 400

    image_file = request.files['image']
    filter_type = request.form.get('filter', 'BLUR')
    
    files = {'image': (image_file.filename, image_file.read(), image_file.mimetype)}
    data = {'filter': filter_type}

    try:
        worker_url = random.choice(WORKER_URLS)
        print(f"Enviando tarefa para o worker: {worker_url}")

        response = requests.post(worker_url, files=files, data=data, timeout=10)

        if response.status_code == 200:
            processed_filename = f"processed_{image_file.filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return jsonify({
                "message": "Imagem processada com sucesso!",
                "filename": processed_filename,
                "download_url": f"/download/{processed_filename}"
            })
        else:
            return jsonify({"error": "Worker falhou ao processar a imagem."}), response.status_code

    except requests.RequestException as e:
        print(f"Erro de comunicação com o worker: {e}")
        return jsonify({"error": "Não foi possível conectar a um worker de processamento."}), 500

# --- Rota para Download ---
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Execução do Servidor ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)