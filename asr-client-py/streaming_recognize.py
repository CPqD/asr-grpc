import client
from client import settings
from client import get_token
import RecognizeService_pb2 as recognizeFields
import os
import threading
import time
import grpc
import queue
from rx.subject import Subject
from rx import operators as ops

class TestStopException(Exception):
    pass

def execute_streaming_recognize():
    stub = client.create_stub()
    client.print_message("Streaming Recognize")
    #export METADATA="x-asr-grpc:general"
        #metadata = (('authorization', 'Bearer ' + access_token),)
    timeout=settings.timeout
    if settings.do_cancel:
       timeout=1

    try:
        get_streaming_requests(stub, client.print_result)
    except grpc._channel._MultiThreadedRendezvous as e:
        client.print_message("Streaming Recognize exception")
        if settings.do_cancel:
            pass
        else:
            print(type(e).__name__)
            raise TestStopException("Finalizando o teste com falha.")
    except Exception as e:
        raise e

def get_streaming_requests(stub, on_event=None):
    client.print_message("Streaming:" + settings.audio_name)
    file_name = settings.audio_name
    audio_file = open(file_name, "rb")
    q_audio = queue.Queue()
    stream = Subject()

    print("Interval: {}".format(settings.chunk_interval))
    print("Size: {}".format(settings.chunk_size))

    # Envia dados codificados para a fila
    def on_next(encoded_data):
        last = False
        if settings.do_cancel > 0:
            settings.do_cancel -= 1
            if settings.do_cancel == 0:
                print("Will Cancel")
                last = True
        if len(encoded_data):
            chunk_msg = recognizeFields.StreamingRecognizeRequest(media=encoded_data, last_packet=last)
            q_audio.put(chunk_msg)
        elif settings.encoding == "WAV":
            print("On next: last chunk")
            chunk_msg = recognizeFields.StreamingRecognizeRequest(media=b'', last_packet=True)
            q_audio.put(chunk_msg)

        #if settings.encoding == "RAW":
        #print(f"Data length: {len(encoded_data)}")
        time.sleep(settings.chunk_interval)

    def on_completed():
        q_audio.put(None)

    def encode_audio(waveform: bytes) -> bytes:
        return waveform

    # Assina o stream e começa a capturar áudio
    stream.pipe(
        ops.map(encode_audio)
    ).subscribe_(on_next=on_next, on_completed=on_completed)

    def reader():
        config = create_streaming_config_request()
        q_audio.put(config)
        chunks = []
        if settings.chunk_size < 0:
            audio_chunk = audio_file.read()
            print("Size: {}".format(len(audio_chunk)))
            chunks.append(audio_chunk)
        else:
            audio_chunk = audio_file.read(settings.chunk_size)
            next_chunk = audio_file.read(settings.chunk_size)
            while next_chunk:
                chunks.append(audio_chunk)
                audio_chunk = next_chunk
                next_chunk = audio_file.read(settings.chunk_size)
        chunks.append([])

        # Stream blocks
        for waveform in chunks:
            try:
                stream.on_next(waveform)
            except BaseException as e:
                stream.on_error(e)
                break
        stream.on_completed()

    # Executa a leitura do audio em uma thread separada (não bloqueia)
    threading.Thread(target=reader, daemon=True).start()

    # Gerador gRPC que envia chunks enquanto chegam na fila
    def request_generator():
        while True:
            chunk = q_audio.get()
            if chunk is None:
                print("<End of Audio>")
                break
            yield chunk

    # Processa a resposta da diarização em tempo real
    try:
        for event in stub.StreamingRecognize(request_generator()):
            if on_event:
                on_event(event)
            else:
                print(f"{event}")
    except Exception as e:
        print(f"Erro no streaming gRPC: {e}")
        raise e

    audio_file.close()

def create_streaming_config_request():
    return recognizeFields.StreamingRecognizeRequest(config=client.get_config())

async def get_message(audio_chunk, last, stop = False):
    return recognizeFields.StreamingRecognizeRequest(media=audio_chunk, stop=stop, last_packet=last)

if __name__ == "__main__":
    try:
        execute_streaming_recognize()
        exit(0)
    except Exception as e:
        exit(1)
