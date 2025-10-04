# Sistema Distribuído de Processamento de Imagens

#### Um sistema onde o cliente envia imagens para um servidor central, que distribui o processamento dessas imagens para vários computadores (workers). Cada worker aplica filtros ou transformações nas imagens de forma paralela e devolve o resultado ao servidor. O cliente pode então baixar as imagens já processadas.

## Como utilizar do sistema?

* Copie o link do repositório e clone numa pasta do máquina local.
```
git clone https://github.com/DuMilo/sistema-de-processamento-imagem.git
```

* Ter Python e o pip instalado é **necessário**

* Instale as dependências:

```
pip install Flask requests Pillow
```

* Na mesma pasta, adicione uma imagem e nomeie-a de "sample_image" (no código tá .jpg, se for outro formato: trocar)

* Abra três terminais:
  
-> No Terminal 1 (Worker 1): Inicie a primeira instância do worker na porta 5001.

```
python worker.py 5001
```

-> No Terminal 2 (Worker 2): Inicie a segunda instância do worker em outra porta, 5002.

```
python worker.py 5002
```

-> No Terminal 3 (Servidor): Inicie o servidor central.

```
python server.py
```

-> Finalmente, no Terminal 3: Execute o cliente para iniciar o processo.

```
python client.py
```

## Tecnologias Usadas

* **Linguagem de Programação**: Python
* **Bibliotecas**: requests, PIL
* **Frameworks**: Flask
* **IDEs**: VSCode
