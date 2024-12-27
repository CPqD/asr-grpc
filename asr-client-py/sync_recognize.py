import client
from client import settings
import RecognizeService_pb2 as recognizeFields
import os

def execute_sync_recognize():
    stub = client.create_stub()

    access_token=settings.sl_token
    meta=settings.metadata
    meta_par=meta_val='x-null'

    if meta:
        meta_par=meta[0:meta.find(':')]
        meta_val=meta[meta.find(':')+1:]
    if access_token:
        metadata = (('authorization', 'Bearer ' + access_token), (meta_par, meta_val),)
        response = stub.Recognize(create_sync_request(), metadata=metadata)
    else:
        response = stub.Recognize(create_sync_request())

    client.print_message("Synchronous Recognize")
    print(response)
    client.print_result(response)

def create_sync_request():
    return recognizeFields.RecognizeRequest(config=client.get_config(), media=get_audio_bytes())


def get_audio_bytes():
    file_name = settings.audio_name
    audio_file = open(file_name, "rb")
    audio_bytes = audio_file.read()
    audio_file.close()
    return audio_bytes


if __name__ == "__main__":
    execute_sync_recognize()
