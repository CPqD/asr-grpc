package br.com.cpqd.asr;

import br.com.cpqd.asr.grpc.*;
import com.google.protobuf.ByteString;
import io.grpc.ManagedChannel;
import lombok.RequiredArgsConstructor;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.List;

@RequiredArgsConstructor
public class SyncRecognize {

    private final RecognizeServiceGrpc.RecognizeServiceBlockingStub stub;
    private final RecognitionConfig.LanguageModel languageModel;
    private final RecognitionConfig.AudioEncoding audioEncoding;
    private final Path audioPath;

    List<RecognitionResult> run() throws IOException {
        FileInputStream inputStream = new FileInputStream(audioPath.toFile());
        RecognizeResponse response = stub.recognize(createRequest(inputStream, createConfig()));
        inputStream.close();
        return response.getResultList();
    }

    private RecognitionConfig createConfig() {
        RecognitionConfig config = RecognitionConfig.newBuilder().addLm(languageModel).setAudioEncoding(audioEncoding)
                .build();
        return config;
    }

    private RecognizeRequest createRequest(InputStream audioInputStream, RecognitionConfig config) throws IOException {
        RecognizeRequest recognizeRequest = RecognizeRequest.newBuilder()
                .setMedia(ByteString.copyFrom(audioInputStream.readAllBytes())).setConfig(config).build();
        return recognizeRequest;
    }
}
