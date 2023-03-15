import grpc
import RecognizeService_pb2_grpc as recognizeService
import RecognizeService_pb2 as recognizeFields


def create_stub():
    channel = grpc.insecure_channel("localhost:8026")
    stub = recognizeService.RecognizeServiceStub(channel)
    return stub


def get_config():
    language_model = recognizeFields.RecognitionConfig.LanguageModel(content_type="text/uri-list",
                                                                     uri="builtin:slm/general")
    return recognizeFields.RecognitionConfig(lm=[language_model],
                                             audio_encoding=recognizeFields.RecognitionConfig.AudioEncoding.WAV)


def print_message(message):
    print("\n#################################################")
    print("############# {} #############".format(message))
    print("#################################################\n")
