# Cliente ASR Python

Este é um exemplo de um cliente desenvolvido em Python para uso do servidor ASR via GRPC.

Versão do **Python** utilizada: `3.10.10`

Versão do **pip** utilizada: `23.0.1`

## Como executar o projeto

1) Crie um ambiente virtual:

```
python3 -m venv venv
```

2) Instale o pacote grpcio-tools:

```
pip install grpcio-tools
```

3) Execute o comando abaixo, substituindo os valores de acordo com seus diretórios, para gerar os arquivos do protobuf

```
python3 -m grpc_tools.protoc -I ../proto/ --python_out=. --pyi_out=. --grpc_python_out=. ../proto/RecognizeService.proto
```

4) Mude o endereço e porta do servidor destino, que podem ser configurados no arquivo `client.py` na linha 7, dentro do
   método `create_stub()`.

```
7 channel = grpc.insecure_channel("localhost:8026")
```

5) Para executar o reconhecimento síncrono, execute o seguinte comando:

```
python3 sync_recognize.py
```

6) Para executar o reconhecimento assíncrono, execute o seguinte comando:

```
python3 streaming_recognize.py
```