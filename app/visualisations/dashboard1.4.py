import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from  dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from statistics import mode
import re, ast
import joblib
import nltk
import keras
#from tensorflow import keras
from keras.models import Sequential
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from nltk.corpus import stopwords
#from nltk import word_tokenize
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

model_name = 'model/enforceability_model.h5'
model = keras.models.load_model(model_name)
tokenizer_name = 'model/enforceability_tokenizer.joblib'
tokenizer = joblib.load(tokenizer_name)


REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
SINGLE_LETTERS_RE = re.compile('\s+[a-zA-Z]\s+')
STOPWORDS = set(stopwords.words('english'))
STOPWORDS.remove('should')
STOPWORDS.add('applicant')
STOPWORDS.add('proponent')
STOPWORDS.add('groundwater')
STOPWORDS.add('water')
STOPWORDS.add('environment')
STOPWORDS.add('act')
STOPWORDS.add('project')
STOPWORDS.add('creek')

# The maximum number of words to be used. (most frequent)
MAX_NB_WORDS = 3000
# Max number of words in each complaint.
MAX_SEQUENCE_LENGTH = 100





def clean_text(text):
    """
        text: a string
        
        return: modified initial string
    """
    text = text.lower() # lowercase text
    text = REPLACE_BY_SPACE_RE.sub(' ', text) # replace REPLACE_BY_SPACE_RE symbols by space in text. substitute the matched string in REPLACE_BY_SPACE_RE with space.
    text = BAD_SYMBOLS_RE.sub('', text) # remove symbols which are in BAD_SYMBOLS_RE from text. substitute the matched string in BAD_SYMBOLS_RE with nothing. 
    text = ' '.join(word for word in text.split() if word not in STOPWORDS) # remove stopwords from text
    return text


def get_es(conditions):
    
    labels = ['1', '2', '3', '4', '5']

    cond=[]
    cond.append(conditions)
    df_new = pd.DataFrame(data=cond,index=None)
    df_new[0] = df_new[0].apply(clean_text)
    df_new[0] = df_new[0].str.replace('\d+', '')
    

    seq = tokenizer.texts_to_sequences(df_new[0].values)
    padded = pad_sequences(seq, maxlen=MAX_SEQUENCE_LENGTH)
    
    pred = model.predict(padded,verbose=0)
    stars = labels[np.argmax(pred)]
    
    return int(stars)

# <------------------------------dash Components Below ------------------------------------------


#external_stylesheets = ['https://codepen.io/anon/pen/mardKv.css']
external_stylesheets = ['external_stylesheets=[dbc.themes.BOOTSTRAP]']
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets=[
#    "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap-grid.min.css"
#]

app = dash.Dash(__name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True, 
    title='Enforceability Score', 
    update_title='Loading...',
    meta_tags=[
    # A description of the app, used by e.g.
    # search engines when displaying search results.
    {
        'name': 'Enforceability Score',
        'content': 'Sentiment Analysis of NSW Planning Conditions for coal mines based on the degree of compulsion or discretion in the conditions terms'
    },
    # A tag that tells Internet Explorer (IE)
    # to use the latest renderer version available
    # to that browser (e.g. Edge)
    {
        'http-equiv': 'X-UA-Compatible',
        'content': 'IE=edge'
    },
    # A tag that tells the browser not to scale
    # desktop widths to fit mobile screens.
    # Sets the width of the viewport (browser)
    # to the width of the device, and the zoom level
    # (initial scale) to 1.
    #
    # Necessary for "true" mobile support.
    
    {
      'name': 'viewport',
      'content': 'width=device-width, initial-scale=1.0'
    }
]
)



card_header = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                className="app-header",
                children=[
                    html.H1('Enforceability Classifier/Predictor', 
                        className="app-header--title", 
                        ),
                    ],
                ),
        ],
    ),            
)


markdown_text = '''### Sample conditions to cut and paste


#### Water Quality

Except as may be expressly provided for by an EPL or in accordance with section 120 of the Protection of the Environment Operations Act 1997 the Proponent shall not discharge any mine water from the site.


#### Water Quantity

The Proponent shall prepare and implement a Water Management Plan to the satisfaction of the DirectorGeneral. 


#### Landholder Compensation

The Applicant shall provide compensatory water supply to any landowner of privatelyowned land whose water entitlements are impacted other than an impact that is negligible as a result of the development in consultation with NoW and to the satisfaction of the DirectorGeneral.


#### Plans, Strategies and Reports

The Proponent shall ensure that it has sufficient water for all stages of the project and if necessary adjust the scale of mining operations to match its licensed water entitlements to the satisfaction of the DirectorGeneral.

'''




app.layout = dbc.Container(
    [

    dcc.Store(id="store"),

    dbc.Row(dbc.Card(card_header)),
    dcc.Tabs(
        
        [
            dcc.Tab(label="Classifier", 
                value="classifier",
                className='custom-tab',
                selected_className='custom-tab--selected', 
                ),
            dcc.Tab(label="Sample Conditions", 
                value="faq",
                className='custom-tab',
                selected_className='custom-tab--selected', 
                ),
            dcc.Tab(label="Corpus Statistics", 
                value="stats",
                className='custom-tab',
                selected_className='custom-tab--selected', 
                ),
        ],
        id="tabs", 
        value="classifier",
        parent_className='custom-tabs',
        className='custom-tabs-container',

    ),
    html.Div(id="tab-content", 
        className="p.para3"),
    ], fluid=False  #, style={'max-width': '1300px'}, #fluid=True,
)


        


@app.callback(Output('tab-content', 'children'),
    [Input("tabs", "value"), Input("store", "data")],
)
def render_tab_content(active_tab,data):

#    if active_tab and data is not None:
        if active_tab == "classifier":
            return dbc.Container(children=[

                dbc.Row(children=[
                
                    dcc.Textarea(
                        id='input_conditions1',
                        className="input_conditions",
                        value='The Proponent shall ensure that all surface water discharges from the site comply with the discharge limits both volume and quality set for the project in any EPL.',
                        placeholder='Add your Condition Text here...',
                        rows=15,
                    ),
                    dcc.Graph(id='ec_gauge1',
                        className="gauge_graph",
                        figure={})
                    ]
                ), 

                dbc.Row(children=[
                    html.Button
                    (
                        id='add_condition_btn1',
                        className="submit_button",
                        children='Submit',
                        style={
                            'display': 'inline-block',
                        }
                    ),]
                ),

                dbc.Row(children=[

                    dcc.Textarea
                        (
                            id='input_conditions2',
                            className="input_conditions",
                            value='This plan must be prepared in consultation with BCD DPIE Water and North West LLS by suitably qualified and experienced persons whose appointment has been approved by the Secretary and be submitted to the Secretary for approval prior to the commencement of construction.',
                            placeholder='Add your Condition Text here...',
                            rows=15,
                    ),
                    dcc.Graph(id='ec_gauge2',
                        className="gauge_graph",
                        figure={})
                    ]
                ),

                dbc.Row(children=[    
                    html.Button
                        (
                            id='add_condition_btn2',
                            className="submit_button",
                            children='Submit',
                            style={
                                'display': 'inline-block',
                            }
                        )
                    ],                #justify="between",align="start"
                ),
            ])

        elif active_tab == 'faq':
            return dbc.Row(children=[

                dcc.Markdown(className='p.para3',children=markdown_text),
                ]
            ),

#    return "No Tab Selected"



@app.callback(
    Output(component_id='ec_gauge1', component_property='figure'),    
    [Input(component_id='add_condition_btn1', component_property='n_clicks'),
    State(component_id='input_conditions1', component_property='value')],
#    prevent_initial_call=True
)


def update_graph1(n_clicks, input_conditions1):
    
    es = 0
    cleaned_text1 = clean_text(str(input_conditions1))
    es = get_es(cleaned_text1)

    # insert model section here
    fig1 = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = es,
        mode = "gauge+number+delta",
        title = {'text': "Enforceability Score"},
        delta = {'reference': 3},
        gauge = {'axis': {'range': [None, 5]},
                 'bar': {'color': "red"},
                 'steps' : [
                     {'range': [0, es], 'color': "red",
                      'range': [(es), 5], 'color': "white",
                     },
                     ],
                 'threshold' : {'line': {'color': "black", 'width': 5}, 'thickness': 0.75, 'value': 2.5}}
        )
    )
    fig1.update_traces(gauge_axis_ticks="inside", selector=dict(type='indicator'))
    fig1.update_traces(number_suffix=" Stars ", selector=dict(type='indicator'))
    fig1.update_traces(gauge_bar_thickness=1, selector=dict(type='indicator'))
    fig1.update_layout(paper_bgcolor = "#e5e4d7"),
    return(fig1)


@app.callback(
    Output(component_id='ec_gauge2', component_property='figure'),    
    [Input(component_id='add_condition_btn2', component_property='n_clicks'),
     State(component_id='input_conditions2', component_property='value')],
     suppress_callback_exceptions=True
#    prevent_initial_call=True
)


def update_graph2(n_clicks, input_conditions2):
    
    es = 0
    cleaned_text2 = clean_text(str(input_conditions2))
    es = get_es(cleaned_text2)

    # insert model section here
    fig2 = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = es,
        mode = "gauge+number+delta",
        title = {'text': "Enforceability Score"},
        delta = {'reference': 3},
        gauge = {'axis': {'range': [None, 5]},
                 'bar': {'color': "red"},
                 'steps' : [
                     {'range': [0, 2], 'color': "lightgrey"},
                     {'range': [2, 4], 'color': "grey"},
                     {'range': [4, 5], 'color': "white"}],
                 'threshold' : {'line': {'color': "black", 'width': 5}, 'thickness': 0.75, 'value': 2.5} }
        ),
        
    )
    fig2.update_traces(number_suffix=" Stars ", selector=dict(type='indicator'))
    fig2.update_traces(gauge_bar_thickness=1, selector=dict(type='indicator'))
    fig2.update_layout(paper_bgcolor = "#e5e4d7"),
    return(fig2)




def main():

    logs_dir = "/home/admin/dockers/masters/app/visualisations/logs/"
#    check_file_writable(logs_dir)
#    
#    setupLogging(' DASH ', logs_dir)
    
    

    


if __name__ == '__main__':
   app.run_server(debug=True,host='192.168.11.6',port=8050)

