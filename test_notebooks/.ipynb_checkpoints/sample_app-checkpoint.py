from dash import html, Input, Output, Dash
import base64
import webbrowser
from threading import Timer
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
