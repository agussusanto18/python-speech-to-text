import os, base64
from flask import Flask, request, render_template, jsonify, make_response
from google.cloud import speech, storage


app = Flask(__name__, static_folder='uploads')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'
bucket_name = 'agusbucket'



def speech_to_text(gcs_uri):
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        sample_rate_hertz=48000,
        language_code="en-US",
        enable_automatic_punctuation=True
    )

    operation = client.recognize(config=config, audio=audio)
    result = ""
    
    for result2 in operation.results:
        result += result2.alternatives[0].transcript
        
    return result


def upload_file(file):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file)
    return "gs://{}/{}".format(bucket_name, file.filename)


@app.route('/', methods=['GET', 'POST'])
def upload():
    result = ""

    if request.method == 'POST':
        uploaded_file = request.files['file']
        try:
            gcs_uri = upload_file(uploaded_file)
            result = speech_to_text(gcs_uri)
        except Exception as e:
            result = str(e)
        
        return make_response(jsonify({'result': result}), 200)

    return render_template('index.html', result=result)


app.run(host='localhost', port=8000)