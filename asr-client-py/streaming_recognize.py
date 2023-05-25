import client
import RecognizeService_pb2 as recognizeFields
import os


def execute_streaming_recognize():
    stub = client.create_stub()
    access_token=os.getenv('SL_TOKEN')
    if access_token:
        metadata = (('authorization', 'Bearer ' + access_token),)
        responses = stub.StreamingRecognize(get_streaming_requests(), metadata=metadata)
    else:
        responses = stub.StreamingRecognize(get_streaming_requests())

    client.print_message("Streaming Recognize")
    for response in responses:
        print(response)


def get_streaming_requests():
    audio_file = open("bank-transfira-8k.wav", "rb")

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
