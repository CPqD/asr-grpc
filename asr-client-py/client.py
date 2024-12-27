import grpc
import pydantic
if pydantic.version.VERSION >= "2":
    from pydantic_settings import BaseSettings
else:
    from pydantic import BaseSettings
import RecognizeService_pb2_grpc as recognizeService
import RecognizeService_pb2 as recognizeFields
import os

class Settings(BaseSettings):
    server_url: str = ""
    sl_token: str = ""
    certificate_file: str = ""
    metadata: str = ""
    use_tls: bool = False
    language_model_uri: str = ""
    audio_name: str = ""
    do_age_class: bool = False
    do_gender_class: bool = False
    do_emotion_class: bool = False
    continuous_mode: bool = False
    do_cancel: int = 0
    timeout: int = 2
    chunk_interval: float = 0.005
    chunk_size: int = 800
    encoding: str = "WAV"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

def create_stub():
    server=settings.server_url
    if len(server) == 0:
        print("Missing Server URL!!! \n")
        exit(1)

    use_tls=os.getenv("USE_TLS")
    if settings.use_tls:
        certificate=settings.certificate_file
        if not certificate:
            certificate="sl-cpqd-com-br.pem"
            print("Missed certificate using: " + certificate)
        f = open(certificate, 'rb').read()
        i=f.decode().find("CN")
        cn=f.decode()[i:]
        cert_cn = cn[5:cn.find('\n')]
        options = (('grpc.ssl_target_name_override', cert_cn,),)
        options += (('grpc.tls_skip_hostname_verification', 'true',),)
        channel_credentials = grpc.ssl_channel_credentials(f)
        print("Secure connection to: " + server)
        channel = grpc.secure_channel(server, channel_credentials, options=options)
    else:
        print("Insecure connection to: " + server)
        channel = grpc.insecure_channel(server)
    stub = recognizeService.RecognizeServiceStub(channel)
    return stub


def get_config():
    language_model = recognizeFields.RecognitionConfig.LanguageModel(content_type="text/uri-list",
                                                                     uri=settings.language_model_uri)
    if settings.encoding == "WAV":
        audio_encoding=recognizeFields.RecognitionConfig.AudioEncoding.WAV
    else:
        audio_encoding=recognizeFields.RecognitionConfig.AudioEncoding.LINEAR16
    return recognizeFields.RecognitionConfig(lm=[language_model],
                                             audio_encoding=audio_encoding,
                                             age_scores_enabled=settings.do_age_class,
                                             gender_scores_enabled=settings.do_gender_class,
                                             emotion_scores_enabled=settings.do_emotion_class,
                                             continuous_mode=settings.continuous_mode)


def print_message(message):
    print("\n#################################################")
    print("############# {} #############".format(message))
    print("#################################################\n")

def print_result(response):
    #print("Event: {}".format(response.event))
    age="null"
    emotion="null"
    gender="null"
    for r in response.result:
            id=r.segment_index
            if len(r.alternatives):
                text=r.alternatives[0].text
                if r.age_score.event == "AGE RESULT":
                    age = r.age_score.age
                if r.gender_score.event == "GENDER RESULT":
                    gender = r.gender_score.gender
                if r.emotion_class.event == "EMOTION RESULT":
                    emotion = r.emotion_class.emotion
                print("{}: age={} gender={} emotion={} - {}".format(id, age, gender, emotion, text))
            else:
                print("{}: status={}".format(id, r.status))
