import client
from client import settings
import RecognizeService_pb2 as recognizeFields
import os


def execute_streaming_recognize():
    stub = client.create_stub()
    access_token=os.getenv('SL_TOKEN')
    meta=settings.metadata
    meta_par=meta_val='x-null'
    if meta:
        meta_par=meta[0:meta.find(':')]
        meta_val=meta[meta.find(':')+1:]
    if access_token:
        metadata = (('authorization', 'Bearer ' + access_token), (meta_par, meta_val),)
        responses = stub.StreamingRecognize(get_streaming_requests(), metadata=metadata)
    else:
        responses = stub.StreamingRecognize(get_streaming_requests())

    client.print_message("Streaming Recognize")
    for response in responses:
        client.print_result(response)


def get_streaming_requests():
    file_name = settings.audio_name
    audio_file = open(file_name, "rb")

    config = create_streaming_config_request()
    yield config

    audio_chunk = audio_file.read(1024)
    next_chunk = audio_file.read(1024)
    while next_chunk:
        yield recognizeFields.StreamingRecognizeRequest(media=audio_chunk, last_packet=False)
        audio_chunk = next_chunk
        next_chunk = audio_file.read(1024)

    yield recognizeFields.StreamingRecognizeRequest(media=audio_chunk, last_packet=True)

    audio_file.close()


def create_streaming_config_request():
    return recognizeFields.StreamingRecognizeRequest(config=client.get_config())


if __name__ == "__main__":
    execute_streaming_recognize()
