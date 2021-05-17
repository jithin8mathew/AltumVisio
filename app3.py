#!/usr/bin/env python
# coding: utf-8
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
from dash_canvas import DashCanvas
from dash_extensions import Download
import dash_daq as daq
import dash_bootstrap_components as dbc
#from dash_extensions.snippets import send_bytes 
import dash_bootstrap_components as dbc
import json
from dash_table import DataTable
from PIL import Image
import PIL
import PIL.Image
import os
from dash_canvas.utils import (array_to_data_url, parse_jsonstring, parse_jsonstring_rectangle,
                              watershed_segmentation)
from skimage import io, color, img_as_ubyte
import colorsys
import io
import cv2
import scipy.misc
import numpy as np
import datetime
import base64
from base64 import decodestring
from urllib.parse import quote as urlquote
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Layout

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config['suppress_callback_exceptions']=True
app.config.suppress_callback_exceptions = True

ROI = ""
primaryImage = ""

buttonStyle= {'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)','padding':'10px','font-family':'Times New Roman'}
NavbuttonStyle= {'text-shadow': '4px 6px 4px rgba(0, 0, 0, 0.5)','background-color':'rgb(97, 98, 99)','padding':'10px 18px','font-family':'Times New Roman','color':'white','border':'none'}

items = [
    dbc.DropdownMenuItem("Item 1"),
    dbc.DropdownMenuItem("Item 2"),
    dbc.DropdownMenuItem("Item 3"),
]
###########################################################################################################################################################
## Top Nav Bar 
app.layout = html.Div([
    html.Div([
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/home.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/info.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'50px'} ),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/phone.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'50px'} ),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/help-circle.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'50px'} ),        
        html.A(html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/rotate-cw.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'50px'} ), href='/'),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/credit-card.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'50px'} ),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/log-in.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),
        ],style={'display':'block','background-color':'rgb(71,75,80)',"position": "fixed",'width':'100%','height':'10%','margin-left': '10%','top':0,'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.9), 0 6px 20px 0 rgba(0, 0, 0, 0.4)'}),
        html.Br(),
        html.Br(),

        html.Div(
                [
                    dbc.DropdownMenu(id='basicImageProcessing',
                        label="Image", color="secondary", className="m-1", children=[dbc.DropdownMenuItem("transform"), dbc.DropdownMenu(children=[dbc.DropdownMenuItem("HSV",id='convertoHSV'), dbc.DropdownMenuItem("HSB"), dbc.DropdownMenuItem("YPbPr"),dbc.DropdownMenuItem("YCbCr"), dbc.DropdownMenuItem("LAB"),],label="color", color="secondary", className="m-1", direction="right"), dbc.DropdownMenuItem("overlay"), dbc.DropdownMenuItem("statistics"),]
                    ),
                    dbc.DropdownMenu(
                        label="operation", color="secondary", className="m-1", children=[dbc.DropdownMenuItem("noise"), dbc.DropdownMenuItem("edges"), dbc.DropdownMenuItem("smooth"), dbc.DropdownMenuItem("sharpen"),dbc.DropdownMenuItem("brightness"),dbc.DropdownMenuItem("contrast"),dbc.DropdownMenuItem("make binary"),dbc.DropdownMenuItem("filter"),]
                    ),
                    dbc.DropdownMenu(
                        label="analyze", color="secondary", className="m-1", children=[dbc.DropdownMenuItem("transform"), dbc.DropdownMenuItem("color"), dbc.DropdownMenuItem("overlay"), dbc.DropdownMenuItem("statistics"),]
                    ),
                    dbc.DropdownMenu(
                        label="overlay", color="secondary", className="m-1", children=[dbc.DropdownMenuItem("transform"), dbc.DropdownMenuItem("color"), dbc.DropdownMenuItem("overlay"), dbc.DropdownMenuItem("statistics"),]
                    ),
                    dbc.DropdownMenu(
                        label="statistics", color="secondary", className="m-1", children=[dbc.DropdownMenuItem("transform"), dbc.DropdownMenuItem("color"), dbc.DropdownMenuItem("overlay"), dbc.DropdownMenuItem("statistics"),]
                    ),
                    dbc.DropdownMenu(
                        label="Preprocessing", color="secondary", className="m-1", children=[dbc.DropdownMenuItem("Extract frames"), dbc.DropdownMenuItem("Image Labeling"), dbc.DropdownMenuItem("Augmentation"), dbc.DropdownMenu(children=[dbc.DropdownMenuItem("convert to YOLO"), dbc.DropdownMenuItem("convert to tf_records"),], label="object detection", color="secondary", className="m-1", direction="right"), dbc.DropdownMenuItem("object detection"), dbc.DropdownMenuItem("statistics"),]
                    ),
                    dbc.DropdownMenu(
                        label="scientific", color="secondary", className="m-1", children=[dbc.DropdownMenuItem("scientific"), dbc.DropdownMenuItem("Augmentation"), dbc.DropdownMenu(children=[dbc.DropdownMenuItem("convert to YOLO"), dbc.DropdownMenuItem("convert to tf_records"),], label="object detection", color="secondary", className="m-1", direction="right"), dbc.DropdownMenuItem("object detection"), dbc.DropdownMenuItem("statistics"),]
                    ),
                    dbc.DropdownMenu(items, label="Info", color="secondary", className="m-1"),
                    dbc.DropdownMenu(items, label="Link", color="secondary", className="m-1"),
                ],
                style={"display": "flex", "flexWrap": "wrap",'margin-left':'470px', 'margin-top':'1px', 'position':'fixed','z-index':'1'},
            ),
                # dcc.Dropdown(
                #                 id='main-ImageDropdown',
                #                 options=[
                #                     {'label': 'Image', 'value': ' '},
                #                     {'label': 'transform', 'value': 'transform'},
                #                     {'label': 'color', 'value': 'color'},
                #                     {'label': 'overlay', 'value': 'overlay'},
                #                     {'label': 'statistics', 'value': 'statistics'},
                #                         ],
                #                 searchable=False,
                #                 value=' ',
                #                 style={'top':10,'margin':'10px','width':'25%','margin-left':'220px','align':'center','color':'black','textAlign':'center','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),
                # dcc.Dropdown(
                #                 id='main-ProcessorDropdown',
                #                 options=[
                #                     {'label': 'operation', 'value': 'op'},
                #                     {'label': 'Detect edges', 'value': 'edges'},
                #                     {'label': 'smooth / shapen', 'value': 'sands'},
                #                     {'label': 'brightness / contrast', 'value': 'candb'},
                #                     {'label': 'noise', 'value': 'noise'},
                #                     {'label': 'make binary', 'value': 'binaryImage'},
                #                     {'label': 'filter', 'value': 'filter'},
                #                         ],
                #                 searchable=False,
                #                 value='op',
                #                 style={'width':'25%','top':10,'margin-left':'270px','align':'center','color':'black','textAlign':'center','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),

                # ]),
###################################################
###################################################
    html.Div([
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/logo.png', 'rb').read()).decode()),width=75),
        #html.Img(src=app.get_asset_url('./assets/logo.png')),
        html.H5("Control panel", className="display-5"),
        #html.Br(),
        # html.P(
        #     "Change parameters and settings here", className="lead"
        # ),
        html.Div(id='sliderRange',style={'display':'block'}),
        html.Div(id='HSVsliderRange',style={'display':'block'}),
        html.Div(id='output-container-range-slider',style={'display':'block'}),
        html.Div(id='output-container-HSVrange-slider',style={'display':'block'}),
        html.Div([
                html.Br(),
                dcc.Dropdown(
                                id='main-functionsDropdown',
                                options=[
                                    {'label': 'kMeans color segmentation', 'value': 'kMeans'},
                                    {'label': 'Resize', 'value': 'resize'},
                                    {'label': 'RGB Color segmentation', 'value': 'ColorSeg'},
                                    {'label': 'Crop Image', 'value': 'crop'},
                                    {'label': 'Image Processing', 'value': 'imageProcessing'},
                                    {'label': 'YOLO', 'value': 'YOLO Annotation'},
                                    {'label': 'Basic operations', 'value': 'BO'},
                                        ],
                                value='kMeans',
                                style={'width':'100%','align':'center','color':'black','textAlign':'center','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),
                ],style={'margin':'5%'}),
        html.Div(id='ColorSegmentationSubsection-img', style={'display':'None'}),
        html.Div([
                dcc.Input(id="ClusterInput", type="number", placeholder="Number of Clusters", style={ 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
                html.Button('Cluster', id='generateCluster', style={'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)','padding':'10px','font-family':'Times New Roman'}),
            ],id='kMeansColorClustering',style={'display':'None'}),
   
        dcc.Loading(
                id="loading-1_23",
                type="default",
        children= [html.Div([
                    html.Br(),
                    html.Div(style={'margin':'15px'}), #,id='imagesize'
                ],id='reduceSizeButton', style={'margin':'10px','display':'block','position':'relative'}),]),

        html.Div([],id='basicOperations'),
        html.Div([], id='basicOperations_sub'),
        html.Div([], id='basicOperations_sub1'),
        html.Div([], id='basicOperations_sub2'),
        html.Div([], id='basicOperations_sub3'),
        html.Div([], id='basicOperations_sub4'),
        html.Div([], id='basicOperations_sub5'),
        html.Div([], id='basicOperations_sub6'),
        html.Div([], id='basicOperations_sub7'),
        html.Div([], id='hue_segmentationThreshold'),
        
    ],
    style={"position": "fixed","top": 0,"left": 0, "bottom": 0, "width": "25%", "padding": "2rem 1rem", "background-color": "rgb(71,75,80)", 'box-shadow': '0 20px 18px 0 rgba(0, 0, 0, 1)'}, #https://www.w3schools.com/w3css/w3css_sidebar.asp
),
################################################################
## end of left menu
## begning of right menu
################################################################

html.Div([
        html.Br(),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/cpu.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/crop.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/delete.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/save.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),

        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/compass.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/edit.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/droplet.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/upload-cloud.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),

        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/rotate-cw.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/rotate-ccw.png','rb').read()).decode()),width=18, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'25px'} ),

        
        html.Div([
                                daq.Knob(
                                    id='my-knob',   
                                    size=80,
                                    min=-3,
                                    max=3,
                                    value=0,
                                    color='black',
                                    #theme={'dark':True,'secondary': '#ffffff',},
                                    theme = {'dark':True,'background-color': '#303030', 'color': 'white', 'font-color':'white'},
                                    #scale={'style':{'font-size':'50px', 'color':'black'}}
                                ),
                                html.Div(id='knob-output')
                            ],id='knob', style={'display':'block','filter':' drop-shadow(-2px 4px 4px rgba(0, 0, 0, 0.9))'}),

        html.Div([
            dcc.Loading(id='histogramLoading',
                    type='default',
                    children=[html.Div([],id='HISTOGRAM',style={'right':5, 'display':'block','top':345,'width':'10%', 'height':'10%','filter':' drop-shadow(-2px 4px 4px rgba(0, 0, 0, 0.9))'}),],
                    ),
            ]),
        

        ],style={'right':5, 'position':'fixed','top':45, 'width':'10%','height':'95%', 'background-color':'rgb(71,75,80)', 'box-shadow': '0 6px 12px 0 rgba(0, 0, 0, 1)'}),
################################################################
## end of right menu
################################################################
###################################################################################################################################################
##############              Begining of HTML main div          
###################################################################################################################################################
html.Div([
    html.Hr(),
    html.H1('Image Processing: AltumVīsiō',style={'text-shadow': '4px 6px 4px rgba(0, 0, 0, 1)','margin-top':'50px'}),
    html.Br(),
    html.H5('Upload your image',style={'display':'block'},id='upload-button'),
    
    html.Div([
      ######    html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/arrow-left.png','rb').read()).decode()),width=28, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'50px','display': 'block'} ),
      dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select color image'),
            #html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/owl.png', 'rb').read()).decode()),width=200, style={'z-index': '-1','position':'absolete','left': '0px',})
        ]),
        style={
            'width': '150%',
            'height': '350px',
            'lineHeight': '350px',
            'borderWidth': '1px',
            'borderStyle': 'none', #outset
            'borderRadius': '15px',
            'textAlign': 'center',
            'margin': '10px',
            'display':'block',
            'transform': 'translate(-20%, -0%)', #https://blog.hubspot.com/website/center-div-css
            'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)',
        },
        multiple=False,
        accept='image/*'
        # max_size= 100000
    ),

    ######      html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets/svgtopng/arrow-right.png','rb').read()).decode()),width=28, style={'filter':' drop-shadow(-2px 2px 2px rgba(0, 0, 0, 0.9))','margin':'10px', 'margin-left':'50px','display': 'block'} ),
    #html.Button('Upload', id='button',style={'display':'block', 'textAlign':'center','position':'absolete','top':'50%','left':'50%'}),
    
          ], style={'textAlign': 'center','display': 'inline-block','position':'relative', 'margin-left': 'auto', 'margin-right': 'auto', 'width': '32.5%','background-image': 'url(https://www.pexels.com/photo/scenic-view-of-agricultural-field-against-sky-during-sunset-325944/)'}, className="five columns"),
        
    html.Div(id='output-image-upload' ,style={'height':'100', 
                                                'width':'38%',
                                                'display': 'relative',
                                                'position':'center',
                                                'align':'center',
                                                'margin-left': 'auto', 
                                                'margin-right': 'auto', 
                                                'padding-left': '40px',
                                                'padding-right': '40px',
                                                'padding-topg': '25px',
                                                # 'z-index':'-1',
                                                'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)'}),

    html.Div([
    html.Img(id='segmentation-img', width=100),
    dcc.Loading(
                id="loading-1_1",
                type="default",
                children= [html.Div(id='basicOperationsOutput', style={'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)', 'margin':'15px', 'top':'300px'}),]
                ),  
    dcc.Loading(
                id="loading-1_22",
                type="default",
                children= [html.Div(id='basicImgeProcessing', style={'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)', 'margin':'15px', 'top':'300px'}),]
                ),    
    
    html.Img(id='ColorSegmentation-img', width=500, style={'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)', 'margin':'15px', 'position':'absolete'}),
    html.Img(id='ColorHSVSegmentation-img', width=500, style={'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)', 'margin':'15px','position':'relative'}),
    html.Img(id='resized-img', width=500, style={'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)', 'margin':'15px'}),
    #html.Img(id='KmeanColorSegmentation-img', width=500),
    html.Div(id='KmeanColorSegmentation-img'),
            html.Div(id='color_range'),
            html.Div(id='container-button-basic'),
            html.Div([html.Button('Save', id='save-output', style={'display':'None'})]), #, Download(id="download")
            html.Br(),
            # html.Div([
            #             html.Button('Download image', id='SAVE', 
            #                 style={'display':'block'
            #                         ,'position':'relative',
            #                         'top': '45%','left': '45%',
            #                         'font-size': '16px',
            #                         'padding': '8px 12px',
            #                         'border-radius': '4px',
            #                         'text-align': 'center',
            #                         'align':'center',
            #                         'color':'black',
            #                         'font-family':'Times New Roman',
            #                         'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)',
            #                         'textAlign':'center'})
            #             ,Download(id="download")
            #         ]),
            html.Br(),
            ]),#className="five columns", style={'height':'100', 'width':'100'}),
 
], style={'textAlign': 'center','background-color': 'rgb(71,75,80)','color': 'white', 'font-family':'Times New Roman','margin-left': '10%','margin-right': 'auto','width': '100%'})
    ], style={'textAlign': 'center','background-color': 'rgb(59, 63, 71)','color': 'white', 'font-family':'Times New Roman','align':'center','margin-top':0,'top':0,'margin':'None','max-width': '100%', 'overflow-x': 'hidden'})
########################################################################################################################################
########################################################################################################################################
# END OF MAIN HTML DIV
########################################################################################################################################
########################################################################################################################################
# def updateAndDisplay():
    


def parse_contents(contents):#, filename, date):
    # return html.Div([
        if contents is not None: 
            data = contents.encode("utf8").split(b";base64,")[1]
            img = io.BytesIO()
            img.write(base64.b64decode(data))
            img.seek(0)
            i = np.asarray(bytearray(img.read()), dtype=np.uint8)
            i = cv2.imdecode(i, cv2.IMREAD_COLOR)
            i = cv2.cvtColor(i, cv2.COLOR_RGB2BGR)
            figu = px.imshow(i, width=920, height=510, binary_string=True)
            figu.update_layout(dragmode="drawrect")
            figu.update_layout(margin=dict(l=0, r=0, t=0, b=0)),
            figu.update_xaxes(showticklabels=False)
            figu.update_yaxes(showticklabels=False)
            Igraph = dcc.Graph(id='multiAnnotation',figure=figu, 
                                    config=config, style= BOStyle)
            return Igraph


@app.callback([Output('output-image-upload', 'children'),Output('upload-image', 'style'),Output('upload-button', 'style')],
              [Input('upload-image', 'contents')])#,

def update_output_div(list_of_contents):#, list_of_names, list_of_dates):
    if list_of_contents is None:
        #print('None triggerred')
        children = None
        return children, {
            'width': '150%',
            'height': '350px',
            'lineHeight': '350px',
            'borderWidth': '1px',
            'borderStyle': 'none', #outset
            'borderRadius': '15px',
            'textAlign': 'center',
            'margin': '10px',
            'display':'block',
            'transform': 'translate(-20%, -0%)', #https://blog.hubspot.com/website/center-div-css
            'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)',
        }, {'display': 'block'}
    if list_of_contents is not None:
        #print('image triggerred')
        children = parse_contents(list_of_contents)#, list_of_names, list_of_dates)
        return children, {'display': 'none'}, {'display': 'none'}


@app.callback([Output('segmentation-img', 'src'),Output('color_range', 'children'),Output('save-output','style')],
              [Input('annot-canvas', 'json_data')],#,Input('upload-image', 'contents')]
              [State('upload-image', 'contents')]) # receive data from canvas, input button and NDVI upload

#@functools32.lru_cache(maxsize=32)
def segmentation(string, content):
    global ROI
    if string:
        data = content.encode("utf8").split(b";base64,")[1]
        img = io.BytesIO()
        img.write(base64.b64decode(data))
        img.seek(0)
        i = np.asarray(bytearray(img.read()), dtype=np.uint8)
        i = cv2.imdecode(i, cv2.IMREAD_COLOR)
        mask = parse_jsonstring_rectangle(string)
        mask = list(np.ravel(mask))
        w,h,x,y = mask[0],mask[1],mask[2],mask[3]
        ROI = cv2.cvtColor(i[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
        r,g,b = cv2.split(ROI)
        rgb_range = [r.min(),r.max(),g.min(),g.max(),b.min(),b.max()]
        
    else:
        raise PreventUpdate
    return array_to_data_url(img_as_ubyte(ROI)) , html.Div([html.Button(r.min(),id='submit-val', style={'background-color':'rgb(255, 115, 115)','display': 'inline-block','color': 'white','padding': '6px 16px','border-radius': '4px','margin': '4px 0px','font-size': '16px'}),
                                                            html.Button(r.max(),id='submit-val', style={'background-color':'rgb(217, 0, 0)','display': 'inline-block','color': 'white','padding': '6px 16px','border-radius': '4px','margin': '4px 0px','font-size': '16px'}),
                                                            html.Button(g.min(),id='submit-val', style={'background-color':'rgb(138, 255, 145)','display': 'inline-block','color': 'white','padding': '6px 16px','border-radius': '4px','margin': '4px 0px','font-size': '16px'}),
                                                            html.Button(g.max(),id='submit-val', style={'background-color':'rgb(16, 156, 25)','display': 'inline-block','color': 'white','padding': '6px 16px','border-radius': '4px','margin': '4px 0px','font-size': '16px'}),
                                                            html.Button(b.min(),id='submit-val', style={'background-color':'rgb(122, 177, 255)','display': 'inline-block','color': 'white','padding': '6px 16px','border-radius': '4px','margin': '4px 0px','font-size': '16px'}),
                                                            html.Button(b.max(),id='submit-val', style={'background-color':'rgb(2, 76, 181)','display': 'inline-block','color': 'white','padding': '6px 16px','border-radius': '4px','margin': '4px 0px','font-size': '16px'}),   
                                                            ]), {'display':'relative'}  

##################################################################################################################
##################################################################################################################
##########################      RGB/ HSV     ####################################################################
##################################################################################################################

@app.callback([Output('ColorSegmentationSubsection-img', 'children'),Output('ColorSegmentationSubsection-img', 'style')],
              [Input('main-functionsDropdown', 'value'),#,Input('upload-image', 'contents')]
              #Input('radio1','value'),
              ])

def colorScheme(mainFunc):
    if mainFunc == 'ColorSeg':
        return html.Div([
                html.Br(),
                        dcc.Dropdown(
                                id='thresholdColor-functionsDropdown',
                                options=[
                                    {'label': 'RGB', 'value': 'RGBColor'},
                                    {'label': 'HSV', 'value': 'HSVColor'},
                                        ],
                                value='RGBColor',
                                style={'width':'50%','align':'center','text-align':'left','color':'black','textAlign':'center','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),
                ],style={'margin':'5%'}), {'display':'block'}
    else:
        return None,{'display':'None'}

@app.callback([Output('sliderRange', 'children'),Output('HSVsliderRange', 'children')],
              [Input('main-functionsDropdown', 'value'),Input('thresholdColor-functionsDropdown', 'value'),#,Input('upload-image', 'contents')]
              ],prevent_initial_call=True,)

def displaySliders(mainFuncColorspace ,colorSpaceOption):
    if mainFuncColorspace == 'ColorSeg':
        if colorSpaceOption == 'RGBColor':
            return html.Div([
                        dcc.RangeSlider(
                            id='red',
                            min=0,
                            max=255,
                            step=1,
                            value=[5, 105],
                            updatemode='drag'
                                        ),
                        dcc.RangeSlider(
                            id='green',
                            min=0,
                            max=255,
                            step=1,
                            value=[200, 255],
                            updatemode='drag'
                                        ),
                        dcc.RangeSlider(
                            id='blue',
                            min=0,
                            max=255,
                            step=1,
                            value=[75, 175],
                            updatemode='drag'
                                        ), #{'display':'None'}
                                        #html.Div(id='output-container-range-slider')
                            ],style={'margin':'5%',}), None
            #return {'display':'block'}, {'display':'None'}
        else:
            raise PreventUpdate

        if colorSpaceOption == 'HSVColor':
            return None, html.Div([
                        dcc.Slider(
                            id='hue',
                            min=0,
                            max=360,
                            step=1,
                            value=340
                                        ),
                        dcc.Slider(
                            id='saturation',
                            min=0,
                            max=100,
                            step=1,
                            value=25
                                        ),
                        dcc.Slider(
                            id='val',
                            min=0,
                            max=100,
                            step=1,
                            value=66
                                        ),
                                        #html.Div(id='output-container-HSVrange-slider')
                            ],style={'margin':'5%'}) 
        else:
            raise PreventUpdate    
    else:
        raise PreventUpdate
    # else:
    #     return [None], [None]

@app.callback(Output('output-container-range-slider', 'children'),
             [Input('main-functionsDropdown', 'value'),Input('red', 'value'),Input('green', 'value'),Input('blue', 'value')],
              prevent_initial_call=True,)

def update_slider(MainColorspaceOptRGB , value, value2, value3):
    if MainColorspaceOptRGB == 'ColorSeg':
        return [html.Div([
                html.Button(value[0], id='submit-val', style={'background-color':'rgb(255, 92, 92)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
                html.Button(value[1], id='submit-val', style={'background-color':'rgb(255, 66, 66)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
                html.Button(value2[0], id='submit-val', style={'background-color':'rgb(208, 235, 89)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
                html.Button(value2[1], id='submit-val', style={'background-color':'rgb(16, 156, 25)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
                html.Button(value3[0], id='submit-val', style={'background-color':'rgb(71, 184, 196)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
                html.Button(value3[1], id='submit-val', style={'background-color':'rgb(0, 96, 122)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
            ])]
    else:
        return [None]

@app.callback(Output('output-container-HSVrange-slider', 'children'),
             [Input('main-functionsDropdown', 'value'), Input('hue', 'value'),Input('saturation', 'value'),Input('val', 'value')],
              prevent_initial_call=True,)

def update_HSVslider(MainColorspaceOptHSV, value, value2, value3):
    if MainColorspaceOptHSV == 'ColorSeg':
        return [html.Div([
                html.Button(value, id='submit-val', style={'background-image': 'linear-gradient(to right, #f6d365 0%, #f6d365 20%, #fda085 40%, #fc5603 60%, #f403fc 80%, #4503fc 100%)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none', 'padding-right':'20px','padding-left':'20px'}),
                html.Button(value2, id='submit-val', style={'background-image': 'linear-gradient(to right, #ffffff 0%, #9342f5 100%)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none','padding-right':'20px','padding-left':'20px'}),
                html.Button(value3, id='submit-val', style={'background-image': 'linear-gradient(to right, #000000 0%, #9342f5 100%)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none','color':'white','padding-right':'20px','padding-left':'20px'}),           
            ])]
    else:
        return [None]

@app.callback(Output('ColorSegmentation-img', 'src'),
              [Input('upload-image', 'contents'),              
              Input('main-functionsDropdown', 'value'),#,Input('upload-image', 'contents')]
              Input('red', 'value'),Input('green', 'value'),Input('blue', 'value'),
              ],prevent_initial_call=True,) 

def segmentColorRange(content, mainFunc, rvalue, gvalue, bvalue): #featureType, , hueValue, SatValue, ValValue
    #print(rvalue)
    if mainFunc == 'ColorSeg':
        if content != None:
            data = content.encode("utf8").split(b";base64,")[1]
            img = io.BytesIO()
            img.write(base64.b64decode(data))
            img.seek(0)
            i = np.asarray(bytearray(img.read()), dtype=np.uint8)
            i = cv2.imdecode(i, cv2.IMREAD_COLOR)
            #hsv = cv2.cvtColor(i, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(i, (rvalue[0], gvalue[0], bvalue[0]), (rvalue[1], gvalue[1],bvalue[1]))
            imask = mask>0
            clrImg = np.zeros_like(i, np.uint8)
            clrImg[imask] = i[imask]
            clrImg = cv2.cvtColor(clrImg, cv2.COLOR_BGR2RGB)
            return array_to_data_url(img_as_ubyte(clrImg)) 
    else:
        raise PreventUpdate

@app.callback(Output('ColorHSVSegmentation-img', 'src'),
              [Input('upload-image', 'contents'),
              
              Input('main-functionsDropdown', 'value'),#,Input('upload-image', 'contents')]
              Input('hue', 'value'),Input('saturation', 'value'),Input('val', 'value')
              ],prevent_initial_call=True,) 


def segmentColorRange(content, mainFunc, h, s, v): #featureType, , hueValue, SatValue, ValValue
    #print(h, s, v)
    if mainFunc == 'ColorSeg':
        if content != None:
            data = content.encode("utf8").split(b";base64,")[1]
            img = io.BytesIO()
            img.write(base64.b64decode(data))
            img.seek(0)
            i = np.asarray(bytearray(img.read()), dtype=np.uint8)
            i = cv2.imdecode(i, cv2.IMREAD_COLOR)
            i = cv2.cvtColor(i, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(i, (0,0,0), tuple(round(i * 255) for i in colorsys.hsv_to_rgb(359/100,0.25,0.66)))
            imask = mask>0
            clrImg = np.zeros_like(i, np.uint8)
            clrImg[imask] = i[imask]
            clrImg = cv2.cvtColor(clrImg, cv2.COLOR_BGR2RGB)
            return array_to_data_url(img_as_ubyte(clrImg)) 
    else:
        raise PreventUpdate

##################################################################################################################
##################################################################################################################
##########################      K-Means     ####################################################################
##################################################################################################################

@app.callback(Output('kMeansColorClustering','style'),
              [Input('main-functionsDropdown', 'value')]) 

def kcluster(option):
    if option == 'kMeans':
        return {'display':'block'}
    else:
        return {'display':'None'}

#@app.callback(Output('KmeanOutput', 'children'),
@app.callback(Output('KmeanColorSegmentation-img', 'children'),
              [Input('upload-image', 'contents'),
             Input('main-functionsDropdown', 'value'),
             Input('ClusterInput', 'value'),#,Input('upload-image', 'contents')]
              Input('generateCluster','n_clicks')]) 

def kMeans(content, mainFunc, nClusters, clicks):
    if mainFunc == 'kMeans':
        try:
            if clicks >= 0:
                data = content.encode("utf8").split(b";base64,")[1]
                img = io.BytesIO()
                img.write(base64.b64decode(data))
                img.seek(0)
                img = np.asarray(bytearray(img.read()), dtype=np.uint8)
                img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                Z = np.float32(img.reshape((-1,3)))
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
                _,labels,centers = cv2.kmeans(Z, nClusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
                labels = labels.reshape((img.shape[:-1]))
                image_div=[]
                for i, c in enumerate(centers):
                    print(c)
                    mask = cv2.inRange(labels, i, i)
                    kernel = np.ones((3,3),np.uint8)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel,iterations=4)

                    mask = np.dstack([mask]*3) # Make it 3 channel
                    ex_img = cv2.bitwise_and(img, mask)
                    ex_img = cv2.cvtColor(ex_img, cv2.COLOR_BGR2RGB)

                    image_div.append(html.Div([
                                            html.Img(src=array_to_data_url(img_as_ubyte(ex_img)),width =300,style={'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)', 'margin':'None', 'padding':'None', 'margin-top':'76%'})
                                            ], className="col-sm"))
                return html.Div([div for div in image_div], className="row")
        except Exception:pass

####################################################################################
###############  SAVE FILE ##################
def send_file(filename,mime_type=None):
    try:
        content = array_to_data_url(img_as_ubyte(ROI))
        data = content.encode("utf8").split(b";base64,")[1]
        imgtowrite = io.BytesIO(base64.decodebytes(data))
        c = base64.b64encode(imgtowrite.read()).decode()
        return dict(content=c, filename=filename,mime_type=mime_type, base64=True)
    except Exception: pass

@app.callback(Output("download", "data"), [Input("SAVE", "n_clicks")])

def func(n_clicks):
    return send_file(str(n_clicks)+".png")

####################################################################################
##########   Image ration @########################

@app.callback(Output('reduceSizeButton','children'),
              [Input('main-functionsDropdown', 'value')])

def setSliderforRatio(val):
    if val == 'resize':
        return html.Div([dcc.Upload(html.Button('Upload HQ File', style=buttonStyle),id='HQuploadButton'),html.Br(),daq.Slider(
                                                                                                    id='ratioSlider',
                                                                                                    min=0,
                                                                                                    max=100,
                                                                                                    step=1,
                                                                                                    value=40,
                                                                                                    handleLabel={"showCurrentValue": True,"label": "Ratio"},
                                                                                                                ), html.Button('Resize', 
                                                                                                                                id='resizeClick', 
                                                                                                                                style=buttonStyle),
                                                                                                                html.Br(),
                                                                                                                html.Div([
                                                                                                                        daq.ToggleSwitch(
                                                                                                                                        id='imageQuality',
                                                                                                                                        label='100% quality save',
                                                                                                                                        value=False,
                                                                                                                                        size=25
                                                                                                                                        ),
                                                                                                                        ],style={'display':'inline-block',
                                                                                                                                'justify-content': 'center',
                                                                                                                                'margin':'4px',                                                                                                                            
                                                                                                                                }),
                                                                                                                html.Div([
                                                                                                                        daq.ToggleSwitch(
                                                                                                                                        id='optm',
                                                                                                                                        label='Optimize and save',
                                                                                                                                        value=False,
                                                                                                                                        size=25
                                                                                                                                        ),
                                                                                                                        ],style={'display':'inline-block',
                                                                                                                                 'margin':'4px',
                                                                                                                                 })
                                                                                                                ])
@app.callback(Output('resized-img', 'src'), #,Output('imageSize','value')]
              [Input('resizeClick','n_clicks'),
              Input('ratioSlider', 'value')],
              [State('main-functionsDropdown', 'value'), 
              State('HQuploadButton', 'contents')]
              ) 

def changeImageRatio(n_clicks, ratio, mainOption, content):
    if content != None:
        data = content.encode("utf8").split(b";base64,")[1]
        img = io.BytesIO()
        img.write(base64.b64decode(data))
        img.seek(0)
        img = Image.open(io.BytesIO(bytearray(img.read())))
        img = img.convert('RGB')
        size =img.size
        reduced_size = int(size[0] * (ratio/100)), int(size[1] * (ratio/100)) 
        im_resized = img.resize(reduced_size, Image.ANTIALIAS)
        if n_clicks != None:
            return array_to_data_url(img_as_ubyte(im_resized))
        

#######################################################################################################################
############## HSV color updater ####################################

@app.callback(Output('basicOperations','children'),
    [Input('main-functionsDropdown','value')])

def editMenu(mainOpt):
    if mainOpt == 'BO':
        return [
                html.Div([
                            html.Div([
                                daq.ToggleSwitch(
                                    id='Grey',
                                    label='Greyscale',
                                    labelPosition='bottom',
                                    color='gray',
                                    size='30',
                                    disabled = False
                            )],style={'display':'inline-block', 'margin':'5px'}),
                            html.Div([
                                daq.ToggleSwitch(
                                    id='blur',
                                    label='Blur',
                                    labelPosition='bottom',
                                    color='gray',
                                    size='30',
                                    disabled = False
                            )],style={'display':'inline-block', 'margin':'5px'}),
                            html.Div([
                                daq.ToggleSwitch(
                                    id='thresh',
                                    label='Threshold',
                                    labelPosition='bottom',
                                    color='gray',
                                    size='30',
                                    disabled = False
                            )],style={'display':'inline-block', 'margin':'5px'}), # inverse image (255/image) , threshold options, binary methods 
                              

                        ]),
                html.Div([
                    html.Div([
                                daq.ToggleSwitch(
                                    id='morph',
                                    label='Morphological operations',
                                    labelPosition='bottom',
                                    color='gray',
                                    size='30',
                                    disabled = False
                            )],style={'display':'inline-block', 'margin':'5px'}),
                    ]),
                html.Div([
                    html.Div([
                                daq.ToggleSwitch(
                                    id='shapeDetection',
                                    label='Detect Shapes',
                                    labelPosition='bottom',
                                    color='gray',
                                    size='30',
                                    disabled = False
                            )],style={'display':'inline-block', 'margin':'5px'}),
                    html.Div([
                                daq.ToggleSwitch(
                                    id='lineDet',
                                    label='Detect Lines',
                                    labelPosition='bottom',
                                    color='gray',
                                    size='30',
                                    disabled = False
                            )],style={'display':'inline-block', 'margin':'5px'}),
                    html.Div([
                                daq.ToggleSwitch(
                                    id='can',
                                    label='Canny Edge',
                                    labelPosition='bottom',
                                    color='gray',
                                    size='30',
                                    disabled = True
                            )],style={'display':'inline-block', 'margin':'5px'}),
                    ]),
        ]

@app.callback(Output('basicOperations_sub','children'),
    [Input('main-functionsDropdown','value'),
    Input('blur','value'),
    Input('thresh','value')],prevent_initial_call=True,)

def returnBOsub(mainOpt, blur, thresh): # 
    if mainOpt == 'BO':
        if blur is True:
            return [dcc.Dropdown(
                        id='simpleBlurthresholdColor-functionsDropdown',
                        options=[
                                {'label': 'Blur', 'value': 'blr'},
                                {'label': 'Gaussian Blur', 'value': 'GSN_blr'},
                                {'label': 'Median Blur', 'value': 'MDN_blr'},
                                {'label': 'Bilateral Blur', 'value': 'BLTRL_blr'},
                                ],
                            value='blr',
                            style={'margin':'4px','width':'150px','display':'inline-block','align':'center','text-align':'left','color':'black','textAlign':'center','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),]
        # else:

        if thresh is True:
            return [dcc.Dropdown(
                        id='simplethresholdColor-functionsDropdown',
                        options=[
                                {'label': 'Binary', 'value': 'binary'},
                                {'label': 'Binary inverse', 'value': 'bin_inv'},
                                {'label': 'TRUNC', 'value': 'trunc'},
                                {'label': 'TOZERO', 'value': 'tozero'},
                                {'label': 'TOZERO inverse', 'value': 'tozero_inv'},
                                ],
                            value='binary',
                            style={'margin':'4px','width':'150px','display':'inline-block','align':'center','text-align':'left','color':'black','textAlign':'center','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),
                    dcc.Checklist(
                            id='adaptiveThresh',
                            options=[
                                    {'label': 'Adaptive Thresholding', 'value': 'adaptive'},
                                    ],
                            #value=['NYC', 'MTL']
                            style={'margin':'8px'} 
                                )  
                    ]


@app.callback(Output('basicOperations_sub1','children'),
    [Input('main-functionsDropdown','value'),
    Input('blur','value'),
    Input('simpleBlurthresholdColor-functionsDropdown','value')],prevent_initial_call=True)

def returnkernelsize(mainOpt1, blur1, blurOption):
    if mainOpt1 == 'BO':
        if blur1 is True:
            if blurOption == 'blr':
                return [dcc.Input(id="blurKernelSize", type="number", placeholder="kernel", style={'margin':'2px','width':'25%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),]
            if blurOption == 'GSN_blr':
                return [dcc.Input(id="GaussianblurKernelSize", type="number", placeholder="kernel", style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
                        dcc.Input(id="sigmaX", type="number", placeholder="SigmaX", style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
                        dcc.Input(id="sigmaY", type="number", placeholder="sigmaY", style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'})]
            if blurOption == 'MDN_blr':
                return [dcc.Input(id="MEdianblurKSize", type="number", placeholder="ksize (odd no), eg: 1",min=1, max=100, step=2, style={'margin':'2px','width':'50%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),]
            if blurOption == 'BLTRL_blr':
                return [dcc.Input(id="Bilaterald", type="number", placeholder="Diameter, Defalut: 9",min=1, max=100, step=1, style={'margin':'2px','width':'50%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
                        dcc.Input(id="Bilateralcolor", type="number", placeholder="sigmaColor: Defalut: 75",min=1, max=100, step=1, style={'margin':'2px','width':'50%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
                        dcc.Input(id="Bilateralspace", type="number", placeholder="sigmaSpace, Defalut: 75",min=1, max=100, step=1, style={'margin':'2px','width':'50%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),]
#######################################################################################################################

@app.callback(Output('basicOperations_sub2','children'),
    [Input('main-functionsDropdown','value'),
    Input('thresh','value'),
    Input('simplethresholdColor-functionsDropdown','value'),
    Input('adaptiveThresh','value')],prevent_initial_call=True)

def returnThreshParameters(mainOpt,thresh,threshOption, adaptiveOption):
    if mainOpt == 'BO':
        if thresh is True:
            #if threshOption == 'binary':
            if adaptiveOption == None: 
                return [html.Div([
                                dcc.Slider(
                                    id='simple_binary_threshold',
                                    min=0,
                                    max=254,
                                    step=1,
                                    value=200,
                                                ),
                                dcc.Slider(
                                    id='simple_binary_maxval',
                                    min=0,
                                    max=254,
                                    step=1,
                                    value=254,
                                                ),
                                    ],style={'margin':'3%'}),
                                dcc.Dropdown(
                                    id='ThresholdingType',
                                    options=[
                                            {'label': 'Binary', 'value': 'cv.THRESH_BINARY'},
                                            {'label': 'Binary inverse', 'value': 'cv.THRESH_BINARY_INV'},
                                            {'label': 'TRUNC', 'value': 'cv.THRESH_TRUNC'},
                                            {'label': 'TOZERO', 'value': 'cv.THRESH_TOZERO'},
                                            {'label': 'OTSU', 'value': 'cv.THRESH_OTSU'},
                                            {'label': 'Triangle', 'value': 'cv.THRESH_TRIANGLE'},
                                            ],
                                        value='cv.THRESH_BINARY',
                                        style={'width':'150px','display':'inline-block','align':'center','color':'black','textAlign':'center','margin':'2px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),
                                 ]

@app.callback(Output('basicOperations_sub3','children'),
    [Input('main-functionsDropdown','value'),
    Input('thresh','value'),
    Input('adaptiveThresh','value')],prevent_initial_call=True)


def adaptiveTresh(mainOpt3, thresh1, threshType):
    if mainOpt3 == 'BO':
        if thresh1 is True:
            if threshType[0] == 'adaptive':
                return [html.Div([
                            dcc.Slider(
                                id='adaptive_binary_thresholdMaxVal',
                                min=0,
                                max=254,
                                step=1,
                                value=200,
                                            ),

                                ],style={'margin':'3%'}),
                            dcc.Dropdown(
                                id='adaptiveMethod',
                                options=[
                                        {'label': 'MEAN C', 'value': 'cv.ADAPTIVE_THRESH_MEAN_C'},
                                        {'label': 'GAUSSIAN C', 'value': 'cv.ADAPTIVE_THRESH_GAUSSIAN_C'},
                                        ],
                                    value='cv.ADAPTIVE_THRESH_MEAN_C',
                                    style={'width':'150px','display':'inline-block','color':'black','textAlign':'center','margin':'2px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),

                            dcc.Dropdown(
                                id='ThresholdingTypeforAdaptive',   
                                options=[
                                        {'label': 'Binary', 'value': 'cv.THRESH_BINARY'},
                                        {'label': 'Binary inverse', 'value': 'cv.THRESH_BINARY_INV'},
                                        ],
                                    value='cv.THRESH_BINARY',
                                    style={'width':'150px','display':'inline-block','align':'center','color':'black','textAlign':'center','margin':'2px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),
                            dcc.Input(id="blockSize", type="number", placeholder="Block Size , Defalut:3", min=3, max = 999, step=2, style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
                            dcc.Input(id="Cvalue", type="number", placeholder="C, Defalut: 2", min=-255, max = 255, step=2, style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
                             ]                

@app.callback(Output('basicOperations_sub4','children'),
    [Input('main-functionsDropdown','value'),
    Input('morph','value'),
    ],prevent_initial_call=True)

def MorphologicalOperations(mainOpt4, morphologyEx):
    if mainOpt4 == 'BO':
        if morphologyEx is True:
            return [html.Div([
                        dcc.Dropdown(
                                    id='MorphTypes',
                                    options=[
                                            {'label': 'Erode', 'value': 'ERODE'},
                                            {'label': 'Dialate', 'value': 'DIALATE'},
                                            {'label': 'Open', 'value': 'OPEN'},
                                            {'label': 'Close', 'value': 'CLOSE'},
                                            {'label': 'Gradient', 'value': 'GRADIENT'},
                                            {'label': 'TopHat', 'value': 'TOPHAT'},
                                            {'label': 'BlackHat', 'value': 'BLACKHAT'},
                                            {'label': 'HitMiss', 'value': 'HITMISS'},
                                            ],
                                        value='ERODE',
                                        style={'width':'150px','display':'inline-block','align':'center','color':'black','textAlign':'center','margin':'2px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),
                        html.Div([
                            dcc.Slider(
                                id='MorphKernelSize',
                                min=0,
                                max=100,
                                step=1,
                                value=5,
                                            ),
                                ],style={'margin':'3%'}),
                        html.Div([
                            dcc.Slider(
                                id='MorphIterations',
                                min=0,
                                max=100,
                                step=1,
                                value=1,
                                            ),
                                ],style={'margin':'1%'}),
                        html.Div([
                                daq.ToggleSwitch(
                                    id='AdvancedMorphOperations',
                                    label='Advanced Morphological operations',
                                    labelPosition='bottom',
                                    color='gray',
                                    size='30',
                                    disabled = False
                            )],style={'display':'inline-block', 'margin':'5px'}),
                ])]

# @app.callback(Output('basicOperations_sub5','children'),
#     [Input('AdvancedMorphOperations','value'),],
#     ,prevent_initial_call=True)

@app.callback(Output('basicOperations_sub5','children'),
    [Input('AdvancedMorphOperations','value'),
    ],prevent_initial_call=True)

def AdvancedMorphOperations(advanceOpt):
    if advanceOpt == True:
        return[
        html.Div([
                dcc.Dropdown(
                            id='MorphShapes',
                            options=[
                                    {'label': 'Rectangular', 'value': 'cv.MORPH_RECT'},
                                    {'label': 'Cross-shaped', 'value': 'cv.MORPH_CROSS'},
                                    {'label': 'Elliptic', 'value': 'cv.MORPH_ELLIPSE'},
                                    ],
                                    value='cv.MORPH_RECT',
                                    style={'width':'150px','display':'inline-block','align':'center','color':'black','textAlign':'center','margin':'2px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),
                ])]


@app.callback(Output('basicOperations_sub6','children'),
    [Input('main-functionsDropdown','value'),
    Input('lineDet','value'),
    ],prevent_initial_call=True)

def detectLine(mainOpt6, line):
    if mainOpt6 == 'BO':
        if line is True:
            return [
            html.Div([
                html.Div([
                                daq.ToggleSwitch(
                                    id='detectline',
                                    label='Standard  --  Probablistic',
                                    labelPosition='bottom',
                                    color='gray',
                                    size='30',
                                    disabled = False
                            )],style={'display':'inline-block', 'margin':'5px'}),            

                ])]

@app.callback(Output('basicOperations_sub7','children'),
    [Input('detectline','value')
    ],prevent_initial_call=True)

def lineParameters(lineOption):
    if lineOption is False or lineOption is None:
        return [html.Div([
            dcc.Input(id="lines", type="number", placeholder="lines, Eg:1", style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),                
            dcc.Input(id="rho", type="number", placeholder="rho, Eg:180", style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
            dcc.Input(id="theta", type="number", placeholder="theta, Eg:150", style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
            html.Div([
                            dcc.Slider(
                                id='lineThreshold',
                                min=0,
                                max=100,
                                step=1,
                                value=1,
                                            ),
                                ],style={'margin':'1%', 'margin-top':'15px'}),
            dcc.Input(id="srn", type="number", placeholder="srn, Eg:0", style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
            dcc.Input(id="stn", type="number", placeholder="stn, Eg:0", style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
            ])]
    if lineOption is True:
        return [html.Div([
            dcc.Input(id="Plines", type="number", placeholder="lines, Eg:1", style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),                
            dcc.Input(id="Prho", type="number", placeholder="rho, Eg:180", style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
            dcc.Input(id="Ptheta", type="number", placeholder="theta, Eg:150", style={'margin':'2px','width':'23%', 'text-align':'left', 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
            html.Div([
                     dcc.Slider(
                        id='linePThreshold',
                        min=0,
                        max=100,
                        step=1,
                        value=1,),
                                ],style={'margin':'1%', 'margin-top':'15px'}),
            html.Div([
                     dcc.Slider(
                        id='lineMinLen',
                        min=0,
                        max=1000,
                        step=1,
                        value=50,),
                                ],style={'margin':'1%'}),
            html.Div([
                     dcc.Slider(
                        id='lineMaxLen',
                        min=0,
                        max=1000,
                        step=1,
                        value=100,),
                                ],style={'margin':'1%'}),
            ])]

# @app.callback(Output('basicOperations_sub7','children'),
#     [Input('lineThreshold','value')
#     ],prevent_initial_call=True)

# vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,5))
# vertical_mask = cv2.morphologyEx(cdstP, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
# cdstP= cv2.dilate(vertical_mask, vertical_kernel, iterations=9)

# def displayImageGraph(i):
#     figu = px.imshow(i, width=920, height=510)
#     figu.update_layout(dragmode="drawrect")
#     figu.update_layout(margin=dict(l=0, r=0, t=0, b=0)),
#     figu.update_xaxes(showticklabels=False)
#     figu.update_yaxes(showticklabels=False)
#     return dcc.Graph(id='multiAnnotation',figure=figu, 
#                     config={
#                             "modeBarButtonsToAdd": [
#                             "drawline",
#                             "drawopenpath",
#                             "drawclosedpath",
#                             "drawcircle",
#                             "drawrect",
#                             "eraseshape",
#                             ]
#                             }, style={'text-align': 'center', 
#                             'position': 'absolute', 
#                             'left': '50%', 
#                             'transform': 'translate(-50%, 10%)',
#                             'height':'510px', 'width':'920px'}), {'display':'None'}

config = {"modeBarButtonsToAdd": 
        [
        "drawline",
        "drawopenpath",
        "drawclosedpath",
        "drawcircle",
        "drawrect",
        "eraseshape",
        ]
        }

BOStyle = {'text-align': 'center', 
           'position': 'absolute', 
           'left': '58%', 
           'transform': 'translate(-50%, 0%)',
           'height':'510px', 'width':'920px',
           'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)'}
global Memory 
Memory = {'grey':False, 'blur':False , 'thresh':False}


@app.callback([Output('basicOperationsOutput','children'), Output('output-image-upload','style')],
            [Input('upload-image', 'contents'),  
            Input('main-functionsDropdown', 'value'),
            Input('Grey','value'),
            Input('blur','value'),
            #Input('blurKernelSize','value'),
            # Input('simpleBlurthresholdColor-functionsDropdown','value'),
            Input('thresh','value'),
              ]
              #[State('GaussianblurKernelSize','value')]
              ,prevent_initial_call=True) 
    

def hypyerFunction(BasicImage, basic , grey,  blur, thresh):#, blurGKS, blurType, ):
    #print('triggerred')
    #Memory ={}
    mainImage = ""
    if BasicImage is not None:
        #print('basic inage not none')
        data = BasicImage.encode("utf8").split(b";base64,")[1]
        img = io.BytesIO()
        img.write(base64.b64decode(data))
        img.seek(0)
        i = np.asarray(bytearray(img.read()), dtype=np.uint8)
        i = cv2.imdecode(i, cv2.IMREAD_COLOR)
        i = cv2.cvtColor(i, cv2.COLOR_RGB2BGR)
        # get image height and width to update plotly layout
    
        if basic == 'BO':
            figu = px.imshow(i, width=920, height=510)
            figu.update_layout(dragmode="drawrect")
            figu.update_layout(margin=dict(l=0, r=0, t=0, b=0)),
            figu.update_xaxes(showticklabels=False),
            figu.update_yaxes(showticklabels=False),
            figu.update_layout({'plot_bgcolor':'rgb(71,75,80)','paper_bgcolor':'rgb(71,75,80)'}),
            Igraph = dcc.Graph(id='multiAnnotation',figure=figu, 
                            config=config, style= BOStyle), {'display':'None'}
            #print(basic)
            if grey == True or Memory['grey']==True:
                #print(grey)
                Memory['grey']=True
                i = cv2.cvtColor(i, cv2.COLOR_RGB2GRAY)
                mainImage = i
                figu = px.imshow(i, width=920, height=510, color_continuous_scale='gray')
                figu.update_layout(dragmode="drawrect")
                figu.update_layout(margin=dict(l=0, r=0, t=0, b=0)),
                figu.update_xaxes(showticklabels=False)
                figu.update_yaxes(showticklabels=False)
                Igraph = dcc.Graph(id='multiAnnotation',figure=figu, 
                                config=config, style= BOStyle), {'display':'None'}
            if blur == True or Memory['blur']==True:
                Memory['blur']=True
                kernel = 5
                mainImage = cv2.blur(mainImage,(kernel,kernel))
                figu = px.imshow(mainImage, width=920, height=510)
                figu.update_layout(dragmode="drawrect")
                figu.update_layout(margin=dict(l=0, r=0, t=0, b=0)),
                figu.update_xaxes(showticklabels=False)
                figu.update_yaxes(showticklabels=False)
                Igraph = dcc.Graph(id='multiAnnotation',figure=figu, 
                                    config=config, style= BOStyle), {'display':'None'}
            if thresh == True or Memory['thresh']==True:
                #print(thresh)
                #print(Memory)
                Memory['thresh']=True
                #print(Memory)
                 
                #mainImage = cv2.cvtColor(mainImage, cv2.COLOR_RGB2GRAY)
                if mainImage != "":
                    ret,threshImage = cv2.threshold(mainImage,127,255,cv2.THRESH_BINARY)
                else:
                    ret,threshImage = cv2.threshold(i,127,255,cv2.THRESH_BINARY)
                threshImage = cv2.cvtColor(threshImage, cv2.COLOR_RGB2BGR)
                mainImage = threshImage
                figu = px.imshow(threshImage, width=920, height=510, binary_string=True)
                figu.update_layout(dragmode="drawrect")
                figu.update_layout(margin=dict(l=0, r=0, t=0, b=0)),
                figu.update_xaxes(showticklabels=False)
                figu.update_yaxes(showticklabels=False)
                Igraph = dcc.Graph(id='multiAnnotation',figure=figu, 
                                    config=config, style= BOStyle), {'display':'None'}

                
                #print(blurGKS)

        
        return Igraph


@app.callback([Output('HISTOGRAM','children')], #, Output('3Dsurface','children')
            [Input('upload-image', 'contents')]
              ,prevent_initial_call=True) 

def HistogramImg(BasicImage):
    if BasicImage is not None:
        data = BasicImage.encode("utf8").split(b";base64,")[1]
        img = io.BytesIO()
        img.write(base64.b64decode(data))
        img.seek(0)
        i = np.asarray(bytearray(img.read()), dtype=np.uint8)
        i = cv2.imdecode(i, cv2.IMREAD_COLOR)
        i = cv2.cvtColor(i, cv2.COLOR_RGB2BGR)
        layout = Layout(
            # plot_bgcolor='rgba(82, 81, 81,1)'
            plot_bgcolor='grey'
        )
        fig = go.Figure(layout = layout)
        for channel, color in enumerate(['red', 'green', 'blue']):
            fig.add_trace(go.Histogram(x=i[..., channel].ravel(), opacity=0.5, marker_color=color, name='%s channel' %color))
        fig.update_layout(showlegend=False)
        fig.update_layout(paper_bgcolor="rgba(82, 81, 81,1)")
        fig.update_layout(barmode='overlay', font=dict(color="white", family="Times New Roman, monospace",))
        fig.update_layout(autosize=False, height=150, width=258)
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0, pad=4),)
        
        fig.update_layout(xaxis = {'showgrid': False}, yaxis = {'showgrid': False }),
        # fig.update_layout(dragmode="drawrect")
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0)),
        # figu.update_xaxes(showticklabels=False)
        # figu.update_yaxes(showticklabels=False)
        Igraph = dcc.Graph(id='multiAnnotation',figure=fig, 
                                    config=config)

        return [Igraph]#, [Igraph2]




@app.callback(Output('hue_segmentationThreshold','children'),
            Input('convertoHSV','n_clicks')
             ,prevent_initial_call=True )

def displayHueThresholdSlider(hsv_buttonClick):
    if hsv_buttonClick == True:
        return [html.Div([
                html.H5('threshold'),
                     dcc.Slider(
                        id='Hsv_segmentatino_Threshold',
                        min=0,
                        max=1,
                        step=0.01,
                        value=0.04,),
                                ],style={'margin':'1%'})]
    else:
        raise PreventUpdate
        # return None 


## @app.callback([Output('basicImgeProcessing','children'), Output('output-image-upload','style')], #, Output('3Dsurface','children') #Output('HISTOGRAM','children'), #[Output('basicImgeProcessing','children'), Output('output-image-upload','style')]
@app.callback(Output('basicImgeProcessing','children'),
            [Input('upload-image', 'contents'), Input('convertoHSV','n_clicks'), Input('Hsv_segmentatino_Threshold','value')],
            prevent_initial_call=True) 

def basicImageProcessing(bip, convertoHSV_, hue_threshold_): # bip: basic image processing
    if convertoHSV_ == True:
        if bip is not None:
            data = bip.encode("utf8").split(b";base64,")[1]
            img = io.BytesIO()
            img.write(base64.b64decode(data))
            img.seek(0)
            i = np.asarray(bytearray(img.read()), dtype=np.uint8)
            i = cv2.imdecode(i, cv2.IMREAD_COLOR)
            # i = cv2.cvtColor(i, cv2.COLOR_RGB2BGR)
            from skimage.color import rgb2hsv
            hsv_img = rgb2hsv(i)
            hue_img = hsv_img[:, :, 0]
            hue_threshold = hue_threshold_
            binary_img = hue_img > hue_threshold
            figu = px.imshow(binary_img, width=920, height=510, binary_string=True)
            figu.update_layout(dragmode="drawrect")
            figu.update_layout(margin=dict(l=0, r=0, t=0, b=0)),
            figu.update_xaxes(showticklabels=False)
            figu.update_yaxes(showticklabels=False)
            Igraph = dcc.Graph(id='multiAnnotation',figure=figu, 
                                    config=config, style= BOStyle)#, {'display':'None'}

            return Igraph
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)

# fonts referenced from here : https://feathericons.com/?query=up
# https://svgtopng.com/
# add waitress