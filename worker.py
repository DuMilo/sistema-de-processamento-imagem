# worker.py

# --- Importações Essenciais ---
# Flask: Para criar nossa aplicação web (API).
# request: Para acessar os dados enviados na requisição (como arquivos e formulários).
# send_file: Para enviar um arquivo como resposta.
# Image, ImageFilter: Do Pillow, para abrir, processar e salvar imagens.
# io: Para manipular os dados da imagem em memória, sem precisar salvar em disco no worker.
# sys: Para ler argumentos da linha de comando (usaremos para definir a porta).
from flask import Flask, request, send_file
from PIL import Image, ImageFilter
import io
import sys

# --- Inicialização da Aplicação Flask ---
app = Flask(__name__)

# --- Rota de Processamento ---
# Define o endpoint '/process' que aceita requisições do tipo POST.
@app.route('/process', methods=['POST'])
def process_image():
    """
    Recebe uma imagem e um tipo de filtro, aplica o filtro e retorna a imagem processada.
    """
    # Verifica se o arquivo da imagem foi enviado na requisição.
    if 'image' not in request.files:
        return "Erro: Nenhuma imagem enviada.", 400

    # Pega o arquivo e o tipo de filtro da requisição.
    file = request.files['image']
    filter_type = request.form.get('filter', 'BLUR').upper() # Padrão para BLUR se não for especificado.

    # Abre a imagem usando o Pillow. file.stream garante que lemos o arquivo em memória.
    image = Image.open(file.stream)
    
    # Aplica o filtro solicitado.
    processed_image = None
    if filter_type == 'BLUR':
        processed_image = image.filter(ImageFilter.BLUR)
    elif filter_type == 'GRAYSCALE':
        # 'L' representa o modo de luminância (escala de cinza).
        processed_image = image.convert('L')
    elif filter_type == 'CONTOUR':
        processed_image = image.filter(ImageFilter.CONTOUR)
    else:
        # Se o filtro não for conhecido, apenas retorna a imagem original.
        processed_image = image

    # Salva a imagem processada em um buffer de bytes em memória.
    # Isso é muito eficiente pois evita escrever no disco do worker.
    byte_arr = io.BytesIO()
    processed_image.save(byte_arr, format='PNG')
    byte_arr.seek(0) # Volta ao início do buffer para que possa ser lido e enviado.

    # Envia o buffer de bytes (a imagem) como resposta da API.
    return send_file(byte_arr, mimetype='image/png')

# --- Execução do Worker ---
if __name__ == '__main__':
    # Permite que a gente defina a porta via linha de comando.
    # Ex: python worker.py 5001
    # Se nenhuma porta for informada, usa a 5001 como padrão.
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    
    # Inicia o servidor do worker. debug=True é útil para desenvolvimento.
    app.run(host='0.0.0.0', port=port, debug=True)