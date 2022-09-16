import os, base64
from flask import Flask, request, render_template
from google.cloud import speech


app = Flask(__name__, static_folder='uploads')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'


def speech_to_text(speech_file_data):
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(content=speech_file_data)

    config = speech.RecognitionConfig(
        sample_rate_hertz=44100,
        language_code="en-US",
        enable_automatic_punctuation=True
    )

    operation = client.recognize(config=config, audio=audio)
    result = ""
    
    for result2 in operation.results:
        result += result2.alternatives[0].transcript
        
    return result


def extract_text(file):
    speech_str = base64.b64encode(file.read())
    speech_str = speech_str.decode('utf-8')
    return speech_to_text(speech_str)


@app.route('/', methods=['GET', 'POST'])
def upload():
    result = ""
    if request.method == 'POST':
        try:
            result = extract_text(request.files['file'])
        except Exception as e:
            result = str(e)

    return render_template('index.html', result=result)


app.run(host='localhost', port=8000)