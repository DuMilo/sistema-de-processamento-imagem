# client_paralelo.py

# --- Importações Essenciais ---
import requests
import os
import threading
import time

# --- Configurações do Cliente ---
SERVER_URL = "http://127.0.0.1:5000"
DOWNLOAD_FOLDER = 'downloads'

# --- Função de Trabalho ---
def enviar_e_baixar_imagem(image_path, filter_to_apply):
    thread_name = threading.current_thread().name

    # 1. VERIFICAR ARQUIVO
    if not os.path.exists(image_path):
        print(f"[{thread_name}] ERRO: Imagem '{image_path}' não encontrada.")
        return

    print(f"[{thread_name}] Enviando '{image_path}' para aplicar o filtro '{filter_to_apply}'...")

    # 2. ENVIAR PARA O SERVIDOR
    try:
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            data = {'filter': filter_to_apply}

            upload_response = requests.post(f"{SERVER_URL}/upload", files=files, data=data)
            upload_response.raise_for_status()

            result = upload_response.json()
            print(f"[{thread_name}] Servidor respondeu: {result['message']}")
            
            processed_filename = result['filename']
            download_url = f"{SERVER_URL}{result['download_url']}"

            # 3. BAIXAR O RESULTADO
            print(f"[{thread_name}] Baixando a imagem processada de: {download_url}")
            download_response = requests.get(download_url)
            download_response.raise_for_status()

            # 4. SALVAR O ARQUIVO FINAL
            output_filename = f"paralelo_downloaded_{processed_filename}"
            
            save_path = os.path.join(DOWNLOAD_FOLDER, output_filename)
            
            with open(save_path, 'wb') as f:
                f.write(download_response.content)
            
            print(f"✅ [{thread_name}] Imagem salva como '{output_filename}'!")

    except requests.RequestException as e:
        print(f"❌ [{thread_name}] Ocorreu um erro na comunicação: {e}")
    except Exception as e:
        print(f"❌ [{thread_name}] Um erro inesperado aconteceu: {e}")

# --- Execução Principal ---
if __name__ == "__main__":
    
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    tarefas_em_paralelo = [
        {'image_path': 'sample_image1.jpg', 'filter_to_apply': 'GRAYSCALE'},
        {'image_path': 'sample_image2.jpg', 'filter_to_apply': 'BLUR'},
    ]
    
    threads = []
    
    print("--- Iniciando o envio de múltiplas tarefas ---")
    start_time = time.time()

    # 1. CRIA E INICIA UMA THREAD PARA CADA TAREFA
    for i, tarefa in enumerate(tarefas_em_paralelo):
        thread = threading.Thread(
            target=enviar_e_baixar_imagem,
            kwargs=tarefa,
            name=f"Worker-Request-{i+1}"
        )
        threads.append(thread)
        thread.start()

    # 2. ESPERA TODAS AS THREADS CONCLUÍREM SEU TRABALHO
    for thread in threads:
        thread.join()

    end_time = time.time()
    
    print("\n--- Todas as tarefas foram concluídas! ---")
    print(f"Tempo total de execução: {end_time - start_time:.2f} segundos.")