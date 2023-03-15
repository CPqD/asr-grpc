# Cliente ASR Java

Este é um exemplo de um cliente desenvolvido em Java para uso do servidor ASR via GRPC.

Versão do **Java** utilizada: `17.0.2`

Versão do **Maven** utilizada: `3.8.4`

## Como executar o projeto

1) Gere o pacote jar executável:
```
mvn package
```

2) Mude o endereço e porta do servidor destino, que podem ser configurados no arquivo `Client.java` na linha 20.
```
20 ManagedChannel channel = createChannel("localhost:8026");
```

3) Para executar o reconhecimento síncrono:
```
java -jar ./target/asr-client-java-jar-with-dependencies.jar 1
```

4) Para executar o reconhecimento assíncrono:
```
java -jar ./target/asr-client-java-jar-with-dependencies.jar 2
```

5) Para executar ambos os reconhecimentos:
```
java -jar ./target/asr-client-java-jar-with-dependencies.jar
```