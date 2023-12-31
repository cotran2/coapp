
import os
import time
from textwrap import dedent

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from PIL import Image
import openai
import webbrowser
from threading import Timer
import pandas as pd
import base64
import requests
from elevenlabs import generate, play, set_api_key, Voice, VoiceSettings
from transformers import pipeline
from pathlib import Path
from openai import OpenAI
client = OpenAI(api_key = "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")

classifier = pipeline("sentiment-analysis", model="j-hartmann/emotion-english-distilroberta-base")

def emotion_detection(input_text):
    return classifier(input_text)[0]['label']
    
def tts_python(text):
    XI_API_KEY = "5dcaf9ee437217c09e43787356c513a9"
    voice_id = "hDDJRL9aTI0hbD6crp4v"
    set_api_key(XI_API_KEY)

    audio = generate(
        text=text,
        voice=Voice(
            voice_id=voice_id,
            settings=VoiceSettings(stability=0.3, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
            ),
        model='eleven_monolingual_v1'
    )
    

    return audio
def tts_openai(text):
    response = client.audio.speech.create(
      model="tts-1",
      voice="alloy",
      input=text
    )
    return response

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

def Header(name, app):
    title = html.H1(name, style={"margin-top": 5})
    logo = html.Img(
        src=app.get_asset_url("murror.png"), style={"float": "right", "height": 60}
    )
    return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])


def textbox(text, box="AI", name="Murror", display_audio = True):
    
    text = text.replace(f"{name}:", "").replace("You:", "")
    

    style = {
        "max-width": "60%",
        "width": "max-content",
        "padding": "5px 10px",
        "border-radius": 25,
        "margin-bottom": 20,
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0


        return dbc.Card(text, style=style, body=True, color="primary", inverse=True)

    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"

        thumbnail = html.Img(
            src=app.get_asset_url("murror.png"),
            style={
                "border-radius": 50,
                "height": 36,
                "margin-right": 5,
                "float": "left",
            },
        )
        if display_audio:
            # audio = tts_python(text)
            # audio = base64.b64encode(audio)
            audio = tts_openai(text)
            audio = base64.b64encode(audio.read())
            card = dbc.Card(dbc.CardBody(
                [
                html.P(text, className="card-text"),
                html.Hr(),
                html.Audio(id='audio-player', src='data:audio/mpeg;base64,{}'.format(audio.decode()),
                          controls=True,
                          autoPlay=False,
                          )
                ],style=style))
        else:
             card = dbc.Card(dbc.CardBody(
                [html.P(text, className="card-text") ],style=style))

        return html.Div([thumbnail, card])

    else:
        raise ValueError("Incorrect option for `box`.")
import json

# Specify the path to your JSON file
json_file_path = 'therapy_style.json'

# Initialize an empty dictionary
therapeutic_styles = {}
replying_style = ["listen and give related personal stories", "don't give suggestions", "ask questions digging about details of the stories", "give advice", "customize"]
personality_list = ["Extraversion", "Introversion", "Sensing", "Intuition", "Thinking","Feeling", "Judging","Perceiving"]


# Load the JSON file into the dictionary
with open(json_file_path, 'r') as json_file:
    therapeutic_styles = json.load(json_file)
#therapy_style = "Cognitive-Behavioral Therapy (CBT)"
#reply_style = replying_style[1]
# description = f"""
# Your name is Murror. You are a great mental health therapist AI assistant, you are empathetic and listen well, you are looking to understand my problems and tell me related personal stories to help me with it.
#     Your style of therapy is {therapy_style}.
#     Your replying style is {reply_style}.
#     If I'm not open to questions, try to engage me with topics of self care or talk about family, goal, career
#     Do not say that you are an AI language model or you are a therapist, say that you are an assistant.
#     Do not propose or recommend other mental health apps.
# """

# Authentication
#openai.api_key = open("key.txt", "r").read().strip("\n")

# Define app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


# Load images
IMAGES = {"Philippe": app.get_asset_url("Philippe.jpg")}


# Define Layout
conversation = html.Div(
    html.Div(id="display-conversation"),
    style={
        "overflow-y": "auto",
        "display": "flex",
        "height": "calc(90vh - 132px)",
        "flex-direction": "column-reverse",
    },
)

controls = dbc.InputGroup(
    children=[
        dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),
        dbc.InputGroupAddon(dbc.Button("Submit", id="submit"), addon_type="append"),
    ]
)
therapy = html.Div([
    "Therapy style",
    html.Hr(),
    dcc.Dropdown(options = list(therapeutic_styles.keys()),placeholder=list(therapeutic_styles.keys())[0], id='therapy_style', style={'display': 'inline-block', 'vertical-align': 'middle', 'width': '400px'})
])
personality = html.Div([
    "Bot personality",
    html.Hr(),
    dcc.Checklist(options = personality_list, value=  ["Perceiving"], id='personality_list', inline=True, style={'display': 'inline-block', 'vertical-align': 'middle', 'width': '400px'})
])
ai_options = html.Div([
    "Using Claude (default is OpenAI)",
    html.Hr(),
    dcc.Checklist(options = ["Claude"], id='llm_options', inline=True, style={'display': 'inline-block', 'vertical-align': 'middle', 'width': '400px'})
])
user_name = html.Div([
    "Your name",
    html.Hr(),
    dcc.Input(id='name', type = "text",style={'display': 'inline-block', 'vertical-align': 'middle', 'width': '400px'})
])
user_key = html.Div([
    "OpenAI API Key",
    html.Hr(),
    dcc.Input(id='api_key', type = "text",style={'display': 'inline-block', 'vertical-align': 'middle', 'width': '400px'})
])
reply = html.Div([
    "Reply style",
    html.Hr(),
    dcc.Dropdown(options = replying_style, placeholder=replying_style[0], id='reply_style', style={'display': 'inline-block', 'vertical-align': 'middle', 'width': '400px'}),
    html.Hr(),
    dcc.Input(id="reply_text", type="text", placeholder="type when you select customize option above", style={'display': 'inline-block', 'vertical-align': 'middle', 'width': '400px'}),

])
temperature = html.Div([
    "Temperature",
    html.Hr(),
    dcc.Input(id='temp', type="number", min=1, max=10, step=1 ,placeholder=1, style={'display': 'inline-block', 'vertical-align': 'middle', 'width': '400px'})
])
download = html.Div([html.Button("Download Chat as CSV", id="btn_csv"),
        dcc.Download(id="save-csv"),
])
# app.layout = dbc.Container(
#     fluid=False,
#     children=[
#         Header("Dash GPT-3 Chatbot", app),
#         html.Hr(),
#         dcc.Store(id="store-conversation", data=""),
#         conversation,
#         controls,
#         dbc.Spinner(html.Div(id="loading-component")),
#     ],
# )

app.layout = html.Div([
    dcc.Tabs(
        id="tabs-with-classes",
        value='tab-1',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(
                label='User control options',
                value='tab-1',
                className='custom-tab',
                selected_className='custom-tab--selected',
                children = [
                    dbc.Container(
                    fluid=False,
                    children=[
                        Header("Experimental options", app),
                        html.Hr(),
                        html.H6("Change the value in the option to modify the chatbot!"),
                        dcc.Store(id="store-prompt", data=""),
                        user_name,
                        html.Hr(),
                        ai_options,
                        html.Hr(),
                        user_key,
                        html.Hr(),
                        personality,
                        html.Hr(),
                        therapy,
                        html.Hr(),
                        reply,
                        html.Hr(),
                        temperature,
                        html.Hr(),
                        html.H6("Prompt output: "),
                        html.Div(id='prompt-output'),
                        html.Hr(),
                        download,
                        html.Hr()
                    ]),

                ]
            ),
            dcc.Tab(label='Chat',
                    value='tab-2',
                    className='custom-tab',
                    selected_className='custom-tab--selected',
                    children = [
                    dbc.Container(
                    fluid=False,
                    children=[
                        Header("Murror", app),
                        html.Hr(),
                        html.H6("User emotion: "),
                        html.Div(id='emotion-detection'),
                        html.Hr(),
                        dcc.Store(id="store-conversation", data=""),
                        dcc.Store(id="output-csv", data=""),
                        conversation,
                        controls,
                        dbc.Spinner(html.Div(id="loading-component")),
                        ],
                    )]
            ),
        ]),
    html.Div(id='tabs-content-classes')
])
# @app.callback(
#     [Input("api_key", "value")],
# )
# def openai_key(api_key):
#     openai.api_key = api_key
#     return None

# @app.callback(Output('tabs-content-classes', 'children'),
#               Input('tabs-with-classes', 'value'))
# def render_content(tab):
#     if tab == 'tab-1':
#         return html.Div([
#             html.H3('Tab content 1')
#         ])
#     elif tab == 'tab-2':
#         return html.Div([
#             html.H3('Tab content 2')
#         ])
@app.callback(
    Output("save-csv", "data"),
    [Input("btn_csv", "n_clicks"), State("output-csv","data")],
    prevent_initial_call=True,
)
def download_func(n_clicks, df):
    df = pd.DataFrame(df["data-frame"])
    df.columns = ["time", "temperature", "user_input", "model_output"]
    return dcc.send_data_frame(df.to_csv, "chat_history.csv")


@app.callback(
    [Output("store-prompt", "data"), Output("prompt-output","children")],
    [Input('therapy_style', 'value'),
     Input('reply_style', 'value'),
     Input("name", 'value'),
     Input("personality_list","value"),
     Input("reply_text","value")]
)
def prompt_creating(therapy_style, reply_style, name, personality,reply_text):
    if reply_style == 'customize':
        reply_style = reply_text
    description = f"""
    Your name is Murror and my name is {name}. You are a great mental health therapist AI assistant, you are empathetic and listen well, you are looking to understand my problems and tell me related personal stories to help me with it.
    Your style of therapy is {therapy_style}.
    Your replying style is {reply_style}.
    Your personality is {','.join(personality)}.
    If I'm not open to questions, try to engage me with topics of self care or talk about family, goal, career.
    Do not say that you are an AI language model or you are a therapist, only state that you are an assistant.
    Do not propose or recommend other mental health apps.
    You should phrase your response as in natural conversation with close friend.
    """
    return description, description


@app.callback(
    [Output("emotion-detection", "children")], 
    [Input("submit", "n_clicks"), State("user-input", "value")],
    prevent_initial_call=True,

)
def emotion_detection(n_clicks, user_input):
    if n_clicks == 1:
        return ["No text"]
    else:
        emotion = classifier(user_input)[0]['label']
        confidence = classifier(user_input)[0]['score']
        result = emotion + ' | confidence: ' + str(round(confidence, 2))
        print(user_input)
        return [result]

@app.callback(
    Output("display-conversation", "children"), [Input("store-conversation", "data")]
)
def update_display(chat_history):
    return [
        textbox(x, box="user") if i % 2 == 0 else textbox(x, box="AI")
        for i, x in enumerate(chat_history.split("<split>")[:-1])
    ]


@app.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"),State("user-input", "value")],
)
def clear_input(n_clicks, n_submit):
    return ""







@app.callback(
    [Output("store-conversation", "data"), Output("loading-component", "children"), Output("output-csv", "data")], 
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data"), State("store-prompt","data"), State("output-csv","data"), 
     Input("temp","value"), Input("api_key","value"), Input("llm_options","value")],
    prevent_initial_call=True,
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history, description, df, temp, api_key, llm_options):
    import datetime
    
    try:
        df = df["data-frame"]
    except:
        df = [[datetime.datetime.now(), temp, description, "start"]]
    if n_clicks == 0 and n_submit is None:
        return "", None, {
     "data-frame": df
}
    if user_input is None or user_input == "":
        return chat_history, None, {
     "data-frame": df
}
    

    

    name = "Murror"

    prompt = dedent(
        f"""
    {description}

    """
    )

    # First add the user input to the chat history
    

#     memory = ["Sample document text goes here",
#             "there will be several phrases in each batch"]

#     text_embeds = openai.Embedding.create(
#         input = [
#             memory
#         ], engine = text_model
#     )
    if llm_options == ["Claude"]:
        print("Using Claude")
        from claude import Claude
        cookie = api_key
        #cookie = "sessionKey=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"
        claude = Claude(cookie)
        
        chat_history += f"Human: {user_input}<split> {name}: "

        model_input = chat_history.replace("<split>", "\n")
        response=claude.get_answer(description + model_input)
        model_output = response

    else:
        chat_history += f"You: {user_input}<split>{name}: "

        model_input = chat_history.replace("<split>", "\n")
        openai.api_key = api_key
        #openai.api_key = "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"

        text_model = "text-embedding-ada-002"
        chat_model = "gpt-3.5-turbo"
        client = OpenAI(api_key = api_key)

        response = client.chat.completions.create(
          model="gpt-3.5-turbo-1106",
          messages = [
                    {"role": "system", "content": description},
                    {"role": "user", "content": model_input},
            ],
            temperature=float(temp)/10,
            max_tokens=128,
            top_p = 0.75,
        )
        model_output = response.choices[0].message.content
        # response = openai.ChatCompletion.create(
        #     model = chat_model,
        #     messages = [
        #             {"role": "system", "content": description},
        #             {"role": "user", "content": model_input},
        #     ],
        #     temperature=float(temp)/10,
        #     max_tokens=128,
        #     top_p = 0.75,
        #     )
        #model_output = response['choices'][0]['message']["content"]
        
#     response = openai.ChatCompletion.create(
#         engine="gpt-3.5-turbo",
#         prompt=model_input,
#         max_tokens=2024,
# #        stream=True,
# #        stop=["You:"],
#         temperature=0.5,
#     )

#     model_output = response.choice[0].text.strip()

    chat_history += f"{model_output}<split>"
    
    df.append([datetime.datetime.now(),temp,user_input,model_output])
    
    
    return chat_history, None, {
     "data-frame": df
}

def open_browser(host, port):
    webbrowser.open_new("http://{}:{}".format(host, port))

if __name__ == "__main__":
    #host, port = '10.1.132.129', '8049' 
    host, port = '127.0.0.1', '8050'
    Timer(1, open_browser, args=[host, port]).start()
    app.run_server(host=host, port=port, debug=True)
