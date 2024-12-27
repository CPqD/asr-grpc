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
pip install -r requirements.txt
pip install grpcio-tools
```

3) Execute o comando abaixo, substituindo os valores de acordo com seus diretórios, para gerar os arquivos do protobuf

```
python3 -m grpc_tools.protoc -I ../proto/ --python_out=. --pyi_out=. --grpc_python_out=. ../proto/RecognizeService.proto
```

4) Configurações: é possível alterar as configurações no arquivo [.env](File:./.env)
```
# ASR Server URL
SERVER_URL="server_ip:port"

# Use a secure channel in connection
USE_TLS="true/false"

# Metadata to be added during connection if format <par>:<value>
METADATA="par:value"

# Certificate file for secure connections
CERTIFICATE_FILE="cert_file_path"

# Configure to send a sl token
SL_TOKEN=""

# Language model URI
LANGUAGE_MODEL_URI="builtin:slm/general"

# Audio for recognition
AUDIO_NAME="audio_file"

# Audio encoding
ENCODING="RAW/WAV"

# Enable classification
DO_AGE_CLASS="true/false"
DO_GENDER_CLASS="true/false"
DO_EMOTION_CLASS="true/false"

# Enable continuos mode
CONTINUOUS_MODE="true/false"

# Do cancel after n chunks
#DO_CANCEL=30

# Control audio chunks for streaming recognize
# to simulate realtime audio use interval = 0.1s
# and raw audio
CHUNK_INTERVAL=0.1
CHUNK_SIZE=800

# gRPC Timeout
TIMEOUT=20
```

5) Para executar o reconhecimento síncrono, execute o seguinte comando:

```
python3 sync_recognize.py
```

6) Para executar o reconhecimento assíncrono, execute o seguinte comando:

```
python3 streaming_recognize.py
```
