from openai import OpenAI
from dotenv import load_dotenv
import speech_recognition as sr
from scipy.io import wavfile
import noisereduce as nr
import playsound
from io import BytesIO
import os

load_dotenv()
client = OpenAI()

def conecta_gpt(mensagens):
    respostas = client.chat.completions.create(
        messages=mensagens,
        model='gpt-3.5-turbo-0125',
        max_tokens=1000,
        temperature=0,
        stream=True
    )
    resp_completa = ""
    for stream_resp in respostas:
        texto = stream_resp.choices[0].delta.content
        if texto:
            resp_completa += texto
    print(f'\nAssistant: {resp_completa}', end="")
    return resp_completa

def melhora_audio(audio):
    rate, data = wavfile.read(audio)
    reduced_noise = nr.reduce_noise(y=data, sr=rate)
    audio_melhorado = 'audios/audio_melhorado.wav'
    wavfile.write(audio_melhorado, rate, reduced_noise)
    return audio_melhorado

def coleta_texto():
    print("""
### Bem vindo ao Audio GPT ###
### fale 'finalizar' para encerrar ###
          """)
    mensagens = []
    while True:
        som = ouvir_microfone()
        som_melhorado = melhora_audio(som)
        texto = transforma_audio(som_melhorado)
        print("\nuser: {}".format(texto))
        #precisa corrigir erros de portugues.
        if texto in ['sair','SAIR','Sair',"finalizar", "Finalizar", "FINALIZAR","Finalizar.",'finalizar.']:
            return None
        mensagens.append({'role': "user", 'content': texto})
        resposta = conecta_gpt(mensagens)
        leitor_de_texto(resposta)
        mensagens.append({'role': 'assistant', 'content': resposta})

def leitor_de_texto(texto):
    resposta = client.audio.speech.create(
        model="tts-1",
        voice='onyx',
        input=texto
    )
    file = "audios/resposta.mp3"
    
    resposta.write_to_file(file)
    playsound.playsound(file)
    

def ouvir_microfone():
    
    #habilita o microfone
    microfone = sr.Recognizer()
    #usando o microfone
    with sr.Microphone() as source:
        microfone.adjust_for_ambient_noise(source)  # Ajusta o nível de ruído ambiental
        microfone.pause_threshold = 1
        print("\nouvindo...")
        audio = microfone.listen(source) #salva na variavel audio o audio do microfone
    
    audio_io = BytesIO(audio.get_wav_data())
    return audio_io

def transforma_audio(audio):
    
    file = open(audio, 'rb')
    
    transcricao = client.audio.transcriptions.create(
    model='whisper-1',
    file = file,
    language='pt',
)
    texto = transcricao.text
    return texto

def inicializando():
    if os.path.isdir('audios') == False:
        os.mkdir('audios')

if __name__ == '__main__':
    inicializando()
    coleta_texto()