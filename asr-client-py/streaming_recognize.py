import client
from client import settings
from client import get_token
import RecognizeService_pb2 as recognizeFields
import os
import time
import grpc

def execute_streaming_recognize():
    stub = client.create_stub()
    access_token=get_token()
    meta=settings.metadata
    meta_par=meta_val='x-null'
    if meta:
        meta_par=meta[0:meta.find(':')]
        meta_val=meta[meta.find(':')+1:]
    if access_token:
        metadata = (('authorization', 'Bearer ' + access_token), (meta_par, meta_val),)
        responses = stub.StreamingRecognize(get_streaming_requests(), metadata=metadata, timeout=settings.timeout)
    else:
        responses = stub.StreamingRecognize(get_streaming_requests(), timeout=settings.timeout)

    client.print_message("Streaming Recognize")

    try:
        for response in responses:
            #print(response)
            client.print_result(response)
    except grpc._channel._MultiThreadedRendezvous as e:
        print(type(e).__name__)
        print(e)
        pass


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
        if settings.do_cancel and i > do_cancel:
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
