# Aplicação demonstrativo para reconhecimento e diarizaçãoi online

Este é um exemplo de uma aplicação Web que captura o microphone e envia para reconhecimento e diarização online.

Versão do **node** utilizada: `v18.19.1`

Versão do **npm** utilizada: `9.6.1`

## Como executar o projeto

1) Instale as dependências:
```
npm instal express                                                                                                                                                                                           1mo
npm install @grpc/grpc-js
npm install mic  
```

2) Mude o endereço e porta do servidor ASR, que podem ser configurados no arquivo `client-grpc.js` na linha 17.
```
17 const client = new recognizeService.RecognizeService('localhost:8026', grpc.credentials.createInsecure());
```

3) Exporte o caminho do arquivo asr-grpc/proto/RecognizeService.proto a partir do diretiório raiz do repositório
```
PROTO_PATH=${PWD}/proto/RecognizeService.proto
```

4) Execute o servidor com o node.js:
```
node ws-streamingRecognize.js
```

5) Realize o reconhecimento abrindo o seguinte endereço no browser:
```
http://localhost:8080
```
