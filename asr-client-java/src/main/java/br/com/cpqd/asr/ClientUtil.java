package br.com.cpqd.asr;

import br.com.cpqd.asr.grpc.RecognitionConfig;
import br.com.cpqd.asr.grpc.RecognizeServiceGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;

public class ClientUtil {

    private ClientUtil(){}
    public static ManagedChannel createChannel(String serverAddress) {
        String[] split = serverAddress.split(":");

        return ManagedChannelBuilder.forAddress(split[0], Integer.valueOf(split[1])).usePlaintext().build();
    }

    public static RecognizeServiceGrpc.RecognizeServiceStub createStub(ManagedChannel channel) {
        return RecognizeServiceGrpc.newStub(channel);
    }

    public static RecognizeServiceGrpc.RecognizeServiceBlockingStub createBlockingStub(ManagedChannel channel) {
        return RecognizeServiceGrpc.newBlockingStub(channel);
    }

    public static RecognitionConfig.LanguageModel createLanguageModelWithURI(String uri, String contentType) {
        return RecognitionConfig.LanguageModel.newBuilder().setUri(uri).setContentType(contentType).build();
    }

    public static RecognitionConfig createConfig(RecognitionConfig.LanguageModel languageModel,
            RecognitionConfig.AudioEncoding audioEncoding) {
        RecognitionConfig config = RecognitionConfig.newBuilder().addLm(languageModel).setAudioEncoding(audioEncoding)
                .build();
        return config;
    }
}
