# client.py

# --- Importações Essenciais ---
# requests: Para enviar a imagem para o servidor e depois baixar o resultado.
# os: Apenas para garantir que o arquivo de imagem de exemplo existe.
import requests
import os

# --- Configurações do Cliente ---
SERVER_URL = "http://127.0.0.1:5000"
IMAGE_PATH = "sample_image.jpg" # Aviso do Milo: muda o nome do arquivo pra esse aqui.
FILTER_TO_APPLY = "GRAYSCALE" # Experimente trocar por 'BLUR' ou 'CONTOUR'

def run_client():
    # Verifica se a imagem de exemplo existe antes de continuar.
    if not os.path.exists(IMAGE_PATH):
        print(f"Erro: Imagem de exemplo '{IMAGE_PATH}' não encontrada.")
        print("Por favor, adicione uma imagem com este nome na pasta e tente novamente.")
        return

    # 1. FAZER UPLOAD DA IMAGEM
    print(f"Enviando '{IMAGE_PATH}' para o servidor para aplicar o filtro '{FILTER_TO_APPLY}'...")
    
    # Precisamos abrir o arquivo em modo de leitura binária ('rb').
    with open(IMAGE_PATH, 'rb') as image_file:
        # Prepara os dados para a requisição POST.
        files = {'image': image_file}
        data = {'filter': FILTER_TO_APPLY}

        try:
            # Envia a requisição de upload.
            upload_response = requests.post(f"{SERVER_URL}/upload", files=files, data=data)
            upload_response.raise_for_status() # Lança um erro se a resposta não for 2xx.

            # Extrai os dados da resposta JSON do servidor.
            result = upload_response.json()
            print("Servidor respondeu:", result['message'])
            
            processed_filename = result['filename']
            download_url = f"{SERVER_URL}{result['download_url']}"

            # 2. BAIXAR A IMAGEM PROCESSADA
            print(f"Baixando a imagem processada de: {download_url}")
            download_response = requests.get(download_url)
            download_response.raise_for_status()

            # Salva a imagem recebida em um novo arquivo.
            with open(f"downloaded_{processed_filename}", 'wb') as f:
                f.write(download_response.content)
            
            print(f"Imagem salva como 'downloaded_{processed_filename}'!")

        except requests.RequestException as e:
            print(f"Ocorreu um erro na comunicação: {e}")
        except Exception as e:
            print(f"Um erro inesperado aconteceu: {e}")

# --- Execução do Cliente ---
if __name__ == "__main__":
    run_client()