import client
from client import settings
from client import get_token
import RecognizeService_pb2 as recognizeFields
import os
import time
import grpc

def execute_streaming_recognize():
    stub = client.create_stub()
    timeout=settings.timeout
    if settings.do_cancel:
        timeout=1
    responses = stub.StreamingRecognize(get_streaming_requests(), timeout=timeout)

    client.print_message("Streaming Recognize")

    try:
        for response in responses:
            #print(response)
            client.print_result(response)
    except grpc._channel._MultiThreadedRendezvous as e:
        if settings.do_cancel:
            pass
        else:
            print(type(e).__name__)
            print(e)
            raise TestStopException("Finalizando o teste com falha.")


def get_streaming_requests():
    file_name = settings.audio_name
    audio_file = open(file_name, "rb")

    config = create_streaming_config_request()
    yield config

    audio_chunk = audio_file.read(settings.chunk_size)
    next_chunk = audio_file.read(settings.chunk_size)
    i = 0;
    while next_chunk:
        yield recognizeFields.StreamingRecognizeRequest(media=audio_chunk, last_packet=False)
        audio_chunk = next_chunk
        next_chunk = audio_file.read(settings.chunk_size)
        if settings.do_cancel and i > settings.do_cancel:
            yield recognizeFields.StreamingRecognizeRequest(stop=True)
            print("Will Cancel")
            break
        i = i + 1
        time.sleep(settings.chunk_interval)

    if settings.do_cancel == 0:
        yield recognizeFields.StreamingRecognizeRequest(media=audio_chunk, last_packet=True)

    audio_file.close()


def create_streaming_config_request():
    return recognizeFields.StreamingRecognizeRequest(config=client.get_config())


if __name__ == "__main__":
    execute_streaming_recognize()
