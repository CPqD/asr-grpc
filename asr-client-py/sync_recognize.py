import client
from client import settings
from client import get_token
import RecognizeService_pb2 as recognizeFields
import os

def execute_sync_recognize():
    stub = client.create_stub()

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
