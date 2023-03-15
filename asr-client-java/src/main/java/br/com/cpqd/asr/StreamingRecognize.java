package br.com.cpqd.asr;

import br.com.cpqd.asr.grpc.*;
import com.google.protobuf.ByteString;
import io.grpc.ManagedChannel;
import io.grpc.stub.StreamObserver;
import lombok.RequiredArgsConstructor;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import static br.com.cpqd.asr.ClientUtil.createConfig;

@RequiredArgsConstructor
public class StreamingRecognize {

    private final RecognizeServiceGrpc.RecognizeServiceStub stub;
    private final RecognitionConfig.LanguageModel languageModel;
    private final RecognitionConfig.AudioEncoding audioEncoding;

    private final Path audioPath;
    private CountDownLatch latch = new CountDownLatch(1);
    private List<RecognitionResult> results = new ArrayList<>();

    List<RecognitionResult> run() throws IOException, InterruptedException {
        StreamingRecognizeRequest configRequest = createConfigRequest();
        StreamObserver<StreamingRecognizeRequest> requestObserver = stub.streamingRecognize(
                createResponseObserver());

        requestObserver.onNext(configRequest);

        InputStream audioInputStream = new FileInputStream(audioPath.toFile());

        int read = 0;
        while (read != -1)
            read = sendAudioRequest(audioInputStream, requestObserver);

        audioInputStream.close();
        requestObserver.onCompleted();

        latch.await(30, TimeUnit.SECONDS);

        return results;
    }

    private int sendAudioRequest(InputStream audioSource, StreamObserver<StreamingRecognizeRequest> requestObserver)
            throws IOException {
        byte[] buffer = new byte[1024];
        int read = audioSource.read(buffer);

        boolean lastPacket = false;

        if (read == -1) {
            lastPacket = true;
        }
        ByteString audio = ByteString.copyFrom(buffer);
        StreamingRecognizeRequest audioRequest = createAudioRequest(audio, lastPacket);
        requestObserver.onNext(audioRequest);
        return read;
    }

    private StreamingRecognizeRequest createConfigRequest() {
        return StreamingRecognizeRequest.newBuilder().setConfig(createConfig(languageModel, audioEncoding)).build();
    }

    private StreamingRecognizeRequest createAudioRequest(ByteString audio, boolean lastPacket) {
        var builder = StreamingRecognizeRequest.newBuilder();
        return builder.setMedia(audio).setLastPacket(lastPacket).build();
    }

    private StreamObserver<StreamingRecognizeResponse> createResponseObserver() {

        return new StreamObserver<>() {

            @Override
            public void onNext(StreamingRecognizeResponse response) {

                RecognitionEvent event = response.getEvent();
                if (event.equals(RecognitionEvent.RECOGNITION_RESULT) || response.hasErrorMessage() ||
                        (!event.equals(RecognitionEvent.START_OF_SPEECH) &&
                                 !event.equals(RecognitionEvent.END_OF_SPEECH) &&
                                 !event.equals(RecognitionEvent.LISTENING))) {
                    results.addAll(response.getResultList());

                    if (response.hasErrorMessage() || response.getResult(0).getLastSegment())
                        latch.countDown();

                }
            }

            @Override
            public void onError(Throwable t) {
                System.out.println("error");
                System.out.println(t.getMessage());
                latch.countDown();
            }

            @Override
            public void onCompleted() {
                System.out.println("finished");
                latch.countDown();
            }
        };
    }
}
