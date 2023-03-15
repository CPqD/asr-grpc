package br.com.cpqd.asr;

import br.com.cpqd.asr.grpc.RecognitionConfig;
import br.com.cpqd.asr.grpc.RecognitionResult;
import br.com.cpqd.asr.grpc.RecognizeServiceGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

import static br.com.cpqd.asr.ClientUtil.*;

public class Client {
    public static final String AUDIO_FILENAME = "hints-carros-8k.wav";
    public static final String SRC_MAIN_RESOURCES = "./src/main/resources";

    public static void main(String[] args) throws IOException, InterruptedException {
        ManagedChannel channel = createChannel("localhost:8026");
        RecognitionConfig.LanguageModel languageModel = createLanguageModelWithURI("builtin:slm/general",
                "text/uri-list");
        Path audioPath = Path.of(SRC_MAIN_RESOURCES, AUDIO_FILENAME);

        if(args.length == 1 && args[0].equals("1"))
            syncRecognize(channel, languageModel, audioPath);
        else if(args.length == 1 && args[0].equals("2"))
            asyncRecognize(channel, languageModel, audioPath);
        else{
            syncRecognize(channel, languageModel, audioPath);
            asyncRecognize(channel, languageModel, audioPath);
        }
    }

    private static void syncRecognize(ManagedChannel channel, RecognitionConfig.LanguageModel languageModel, Path audioPath)
            throws IOException {
        RecognizeServiceGrpc.RecognizeServiceBlockingStub blockingStub = createBlockingStub(channel);

        SyncRecognize syncRecognize = new SyncRecognize(blockingStub, languageModel,
                RecognitionConfig.AudioEncoding.WAV, audioPath);
        List<RecognitionResult> recognitionResults = syncRecognize.run();

        System.out.println("################# Sync Recognize #################");

        for (RecognitionResult result : recognitionResults)
            System.out.println(result);
    }

    private static void asyncRecognize(ManagedChannel channel, RecognitionConfig.LanguageModel languageModel, Path audioPath)
            throws IOException, InterruptedException {
        RecognizeServiceGrpc.RecognizeServiceStub stub = createStub(channel);
        StreamingRecognize streamingRecognize = new StreamingRecognize(stub, languageModel,
                RecognitionConfig.AudioEncoding.WAV, audioPath);
        List<RecognitionResult> recognitionResults = streamingRecognize.run();

        System.out.println("################# Streaming Recognize #################");

        for (RecognitionResult result : recognitionResults)
            System.out.println(result);
    }


}