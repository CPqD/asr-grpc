import client
import RecognizeService_pb2 as recognizeFields


def execute_sync_recognize():
    stub = client.create_stub()
    response = stub.Recognize(create_sync_request())

    client.print_message("Synchronous Recognize")
    print(response)


def create_sync_request():
    return recognizeFields.RecognizeRequest(config=client.get_config(), media=get_audio_bytes())


def get_audio_bytes():
    audio_file = open("bank-transfira-8k.wav", "rb")
    audio_bytes = audio_file.read()
    audio_file.close()
    return audio_bytes


if __name__ == "__main__":
    execute_sync_recognize()
