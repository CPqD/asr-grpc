import grpc
from meta_interceptor import MetaInterceptor
import pydantic
if pydantic.version.VERSION >= "2":
    from pydantic_settings import BaseSettings
else:
    from pydantic import BaseSettings
import RecognizeService_pb2_grpc as recognizeService
import RecognizeService_pb2 as recognizeFields
import os
import requests

class Settings(BaseSettings):
    server_url: str = ""
    sl_token: str = ""
    certificate_file: str = ""
    metadata: str = ""
    use_tls: bool = False
    language_model_uri: str = ""
    definition_file: str = ""
    grammar_id: str = ""
    audio_name: str = ""
    do_age_class: bool = False
    do_gender_class: bool = False
    do_emotion_class: bool = False
    continuous_mode: bool = False
    recognition_timeout: int = 10000
    do_cancel: int = 0
    timeout: int = 2
    chunk_interval: float = 0.005
    chunk_size: int = -1
    encoding: str = "WAV"
    token_url: str = ""
    token_user: str = ""
    token_password: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

def get_token():
    if len(settings.sl_token):
        return settings.sl_token
    if len(settings.token_url) == 0:
        return ""
    response=requests.post(settings.token_url, auth=(settings.token_user, settings.token_password))
    if response.ok:
        return response.json()['access_token']
    raise Exception("Fail to get token!")

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
        options = (('','',),)
        options += (('grpc.tls_skip_hostname_verification', 'true',),)
        channel_credentials = grpc.ssl_channel_credentials(f)
        print("Secure connection to: " + server)
        channel = grpc.secure_channel(server, channel_credentials, options=options)
    else:
        print("Insecure connection to: " + server)
        channel = grpc.insecure_channel(server)
    stub = recognizeService.RecognizeServiceStub(channel)
    token = get_token()
    if token or settings.metadata:
        print("Token:" + token)
        print("Metadata:" + settings.metadata)
        interceptor = MetaInterceptor(token, settings.metadata)
        channel = grpc.intercept_channel(channel, interceptor)
        stub = recognizeService.RecognizeServiceStub(channel)
    return stub


def get_config():
    if len(settings.definition_file):
        with open(settings.definition_file, "r") as f:
            language_model = recognizeFields.RecognitionConfig.LanguageModel(content_type="application/octet-stream",
                                                                             definition=f.read(),
                                                                             id=settings.grammar_id)
    else:
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
                                             recognition_timeout= settings.recognition_timeout,
                                             continuous_mode=settings.continuous_mode)


def print_message(message):
    print("\n#################################################")
    print("############# {} #############".format(message))
    print("#################################################\n")

def trunc_time(t):
    return round(t, 2)

def print_result(response):
    def get_status(status):
        if status == 0:
           return "NONE"
        elif status == 1:
           return "PROCESSING"
        elif status == 2:
           return "RECOGNIZED"
        elif status == 3:
           return "NO_MATCH"
        elif status == 4:
           return "NO_INPUT_TIMEOUT"
        elif status == 5:
           return "MAX_SPEECH"
        elif status == 6:
           return "EARLY_SPEECH"
        elif status == 7:
           return "RECOGNITION_TIMEOUT"
        elif status == 8:
           return "NO_SPEECH";
        elif status == 9:
           return "CANCELED"
        elif status == 10:
           return "FAILURE"
    if response.event == 7:
        print("| LISTENING |")
    elif response.event == 1:
        print("| START_OF_SPEECH |")
    elif response.event == 2:
        print("| END_OF_SPEECH |")
    elif response.event == 4:
        print("| FAILURE |")
    elif response.event == 5:
        print("| TIMEOUT |")
    elif response.event == 6:
        print("| INVALID_REQUEST |")
    elif response.event == 3:
        print("| RESULT |")
        age="null"
        emotion="null"
        gender="null"
        for r in response.result:
                id=r.segment_index
                speaker = "unknown"
                if r.HasField('diarization_result'):
                    speaker = r.diarization_result.speaker
                print(f"  {id}: status={get_status(r.status)}")
                if len(r.alternatives):
                    start = r.start_time
                    end = r.end_time
                    text=r.alternatives[0].text
                    if r.age_score.event == "AGE RESULT":
                        age = r.age_score.age
                    if r.gender_score.event == "GENDER RESULT":
                        gender = r.gender_score.gender
                    if r.emotion_class.event == "EMOTION RESULT":
                        emotion = r.emotion_class.emotion
                    print(f"  {id} [{trunc_time(start)}-{trunc_time(end)}]: age={age} gender={gender} emotion={emotion} speaker={speaker} - {text}")
                else:
                    print(f"  {id}: status={get_status(r.status)}")
