# server.py

# --- Importações Essenciais ---
# Flask: Para criar a API do servidor.
# request, jsonify: Para lidar com requisições e respostas JSON.
# send_from_directory: Para permitir o download de arquivos de uma pasta específica.
# os: Para interagir com o sistema de arquivos (criar pastas, etc).
# requests: Para que o servidor possa atuar como um cliente e se comunicar com os workers.
# random: Para escolher um worker aleatoriamente.
from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import random

# --- Configuração Inicial ---
app = Flask(__name__)
UPLOAD_FOLDER = 'processed_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Lista dos nossos workers. Em um sistema real, isso seria descoberto dinamicamente.
WORKER_URLS = [
    "http://127.0.0.1:5001/process",
    "http://127.0.0.1:5002/process",
    # Adicione mais workers aqui se iniciar mais instâncias.
]

# Garante que a pasta para salvar as imagens processadas exista.
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Rota de Upload e Distribuição ---
@app.route('/upload', methods=['POST'])
def upload_and_distribute():
    """
    Recebe a imagem do cliente, distribui para um worker e salva o resultado.
    """
    if 'image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada."}), 400

    image_file = request.files['image']
    filter_type = request.form.get('filter', 'BLUR')
    
    # Prepara os dados para enviar ao worker.
    # O arquivo precisa ser passado no dicionário 'files'.
    files = {'image': (image_file.filename, image_file.read(), image_file.mimetype)}
    data = {'filter': filter_type}

    try:
        # Escolhe um worker aleatoriamente da lista.
        worker_url = random.choice(WORKER_URLS)
        print(f"Enviando tarefa para o worker: {worker_url}")

        # Envia a requisição para o worker e aguarda a resposta.
        # Um timeout é uma boa prática para não esperar indefinidamente.
        response = requests.post(worker_url, files=files, data=data, timeout=10)

        # Se a resposta do worker for bem-sucedida (código 200 OK)...
        if response.status_code == 200:
            # Define um nome para o arquivo processado.
            processed_filename = f"processed_{image_file.filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
            
            # Salva o conteúdo da resposta (a imagem) no disco.
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            # Informa ao cliente o sucesso e como baixar a imagem.
            return jsonify({
                "message": "Imagem processada com sucesso!",
                "filename": processed_filename,
                "download_url": f"/download/{processed_filename}"
            })
        else:
            # Se o worker falhar, repassa o erro.
            return jsonify({"error": "Worker falhou ao processar a imagem."}), response.status_code

    except requests.RequestException as e:
        # Se não conseguir se conectar ao worker.
        print(f"Erro de comunicação com o worker: {e}")
        return jsonify({"error": "Não foi possível conectar a um worker de processamento."}), 500

# --- Rota para Download ---
@app.route('/download/<filename>')
def download_file(filename):
    """
    Permite que o cliente baixe a imagem processada.
    """
    # Usa uma função segura do Flask para servir arquivos de um diretório conhecido.
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Execução do Servidor ---
if __name__ == '__main__':
    # O servidor principal rodará na porta 5000.
    app.run(host='0.0.0.0', port=5000, debug=True)