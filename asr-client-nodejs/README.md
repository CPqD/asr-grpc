# Cliente ASR NodeJS

Este é um exemplo de um cliente desenvolvido em NodeJS para uso do servidor ASR via GRPC.

Versão do **node** utilizada: `16.19.1`

Versão do **npm** utilizada: `9.6.1`

## Como executar o projeto

1) Instale as dependências:
```
npm install @grpc/grpc-js
```

2) Mude o endereço e porta do servidor destino, que podem ser configurados no arquivo `client-grpc.js` na linha 17.
```
17 const client = new recognizeService.RecognizeService('localhost:8026', grpc.credentials.createInsecure());
```

3) Para executar o reconhecimento síncrono:
```
node syncRecognize.js
```

4) Para executar o reconhecimento assíncrono:
```
node streamingRecognize.js
```