from dash import html, Input, Output, Dash
import base64
import webbrowser
from threading import Timer
import requests

def tts_api(text):

    CHUNK_SIZE = 1024
    voice_id = "hDDJRL9aTI0hbD6crp4v"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    XI_API_KEY = "7b9879f9e2b120bea4cf089b2ae47ef4"

    headers = {
      "Accept": "audio/mpeg",
      "Content-Type": "application/json",
      "xi-api-key": XI_API_KEY
    }

    data = {
      "text": text,
      "model_id": "eleven_monolingual_v1",
      "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
      }
    }

    response = requests.post(url, json=data, headers=headers)
    with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)



app = Dash(__name__)

# Encode the local audio file.
sound_filename = 'output.mp3'  # replace with your own .mp3 file
encoded_sound = base64.b64encode(open(sound_filename, 'rb').read())


app.layout = html.Div(children=[
    html.H1(children='Demo for Audio with Dash'),

    html.Div(children='''
        Click the button to play your local .mp3 sounds.
    '''),


    #html.Button(id="button1", children="Click me for sound"),
    html.Audio(id='audio-player', src='data:audio/mpeg;base64,{}'.format(encoded_sound.decode()),
                          controls=True,
                          autoPlay=False,
                          ),])
    #html.Div(id="placeholder", style={"display": "none"})])

# app.clientside_callback(
#     """
#     function(n) {
#       var audio = document.querySelector('#audio-player');
#       if (!audio){
#         return -1;
#       }
#       audio.play();
#       return '';
#    }
#     """, Output('placeholder', 'children'), [Input('button1', 'n_clicks')],
#     prevent_initial_call=True
# )

def open_browser(host, port):
    webbrowser.open_new("http://{}:{}".format(host, port))

if __name__ == "__main__":
    host, port = '10.1.132.129', '8050'
    Timer(1, open_browser, args=[host, port]).start()
    app.run_server(host=host, port=port, debug=True)
