
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



def Header(name, app):
    title = html.H1(name, style={"margin-top": 5})
    logo = html.Img(
        src=app.get_asset_url("murror.png"), style={"float": "right", "height": 60}
    )
    return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])


def textbox(text, box="AI", name="Murror"):
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
        textbox = dbc.Card(text, style=style, body=True, color="light", inverse=False)

        return html.Div([thumbnail, textbox])

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
                        dcc.Store(id="store-conversation", data=""),
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
    [Output("store-prompt", "data"),Output("prompt-output","children")],
    [Input('therapy_style', 'value'),
     Input('reply_style', 'value'),
     Input("name", 'value'),
     Input("personality_list","value"),
     Input("reply_text","value")]
)
def prompt_creating(therapy_style, reply_style, name, personality,reply_stype):
    if reply_stype == 'type':
        reply_stype = reply_text
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
    Output("display-conversation", "children"), [Input("store-conversation", "data")]
)
def update_display(chat_history):
    return [
        textbox(x, box="user") if i % 2 == 0 else textbox(x, box="AI")
        for i, x in enumerate(chat_history.split("<split>")[:-1])
    ]


@app.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks, n_submit):
    return ""


@app.callback(
    [Output("store-conversation", "data"), Output("loading-component", "children")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data"), State("store-prompt","data"), Input("temp","value"), Input("api_key","value")],
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history, description, temp, api_key):
    if n_clicks == 0 and n_submit is None:
        return "", None

    if user_input is None or user_input == "":
        return chat_history, None
    #openai.api_key = api_key
    openai.api_key = "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"

    print(temp)
    text_model = "text-embedding-ada-002"
    chat_model = "gpt-3.5-turbo"

    name = "Murror"

    prompt = dedent(
        f"""
    {description}

    """
    )

    # First add the user input to the chat history
    chat_history += f"You: {user_input}<split>{name}: "

    model_input = chat_history.replace("<split>", "\n")

#     memory = ["Sample document text goes here",
#             "there will be several phrases in each batch"]

#     text_embeds = openai.Embedding.create(
#         input = [
#             memory
#         ], engine = text_model
#     )


    response = openai.ChatCompletion.create(
        model = chat_model,
        messages = [
                {"role": "system", "content": description},
                {"role": "user", "content": model_input},
        ],
        temperature=float(temp)/10,
        max_tokens=2024,
        top_p = 0.75,
        )
    model_output = response['choices'][0]['message']["content"]
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
    return chat_history, None

def open_browser(host, port):
    webbrowser.open_new("http://{}:{}".format(host, port))

if __name__ == "__main__":
    host, port = '127.0.0.1', '8050'
    Timer(1, open_browser, args=[host, port]).start()
    app.run_server(host=host, port=port, debug=True)
