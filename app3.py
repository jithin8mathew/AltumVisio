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


app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True
app.config.suppress_callback_exceptions = True

ROI = ""
primaryImage = ""

buttonStyle= {'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)','padding':'10px','font-family':'Times New Roman'}
NavbuttonStyle= {'text-shadow': '4px 6px 4px rgba(0, 0, 0, 0.5)','background-color':'rgb(97, 98, 99)','padding':'10px 18px','font-family':'Times New Roman','color':'white','border':'none'}
#,'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)'
###########################################################################################################################################################
app.layout = html.Div([
    html.Div([
        html.Button('Home', style=NavbuttonStyle),
        html.Button('About', style=NavbuttonStyle),
        html.Button('Contact', style=NavbuttonStyle),
        html.Button('Help', style=NavbuttonStyle),
        # dbc.Button([html.I(className="fa fa-smile-wink mr-2"), "Click here"]),
        #html.I(className="fa-diagnoses",style={"font-size":"36px",'olor'}),
        ],style={'display':'inline-block','background-color':'rgb(56, 59, 79)',"position": "fixed",'width':'100%','height':'5%','left':0,'top':0,'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.9), 0 6px 20px 0 rgba(0, 0, 0, 0.4)'}),
###################################################
###################################################
    html.Div([
        html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets\\logo.png', 'rb').read()).decode()),width=100),
        #html.Img(src=app.get_asset_url('./assets/logo.png')),
        html.H2("Control panel", className="display-4"),
        html.Br(),
        html.P(
            "Change parameters and settings here", className="lead"
        ),
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
                                    {'label': 'thresh', 'value': 'thresholding'},
                                        ],
                                value='kMeans',
                                style={'width':'100%','align':'center','color':'black','textAlign':'center','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.09)'}),
                ],style={'margin':'5%'}),
        html.Div(id='ColorSegmentationSubsection-img', style={'display':'None'}),
        html.Div([
                dcc.Input(id="ClusterInput", type="number", placeholder="Number of Clusters", style={ 'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)', 'padding':'12px','font-family':'Times New Roman'}),
                html.Button('Cluster', id='generateCluster', style={'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)','padding':'10px','font-family':'Times New Roman'}),
            ],id='kMeansColorClustering',style={'display':'None'}),
        html.Div([
            html.Br(),
            html.Div(style={'margin':'15px'}), #,id='imagesize'
            ],id='reduceSizeButton', style={'margin':'10px','display':'block','position':'relative'})
        
    ],
    style={"position": "fixed","top": 0,"left": 0, "bottom": 0, "width": "25%", "padding": "2rem 1rem", "background-color": "gray", 'box-shadow': '0 20px 18px 0 rgba(0, 0, 0, 1)'}, #https://www.w3schools.com/w3css/w3css_sidebar.asp
),          
###################################################################################################################################################
html.Div([
    html.Hr(),
    html.H1('Image Processing: AltumVīsiō',style={'text-shadow': '4px 6px 4px rgba(0, 0, 0, 1)','margin-top':'50px'}),
    html.Br(),
    html.H2('Upload your image',style={'display':'block'},id='upload-button'),
    html.Div([
      dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select color image'),
            #html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open('assets\\owl.png', 'rb').read()).decode()),width=200, style={'z-index': '-1','position':'absolete','left': '0px',})
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
    
    #html.Button('Upload', id='button',style={'display':'block', 'textAlign':'center','position':'absolete','top':'50%','left':'50%'}),
    
          ], style={'textAlign': 'center','display': 'block','position':'relative', 'margin-left': 'auto', 'margin-right': 'auto', 'width': '32.5%','background-image': 'url(https://www.pexels.com/photo/scenic-view-of-agricultural-field-against-sky-during-sunset-325944/)'}, className="five columns"),
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
                                                'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)'}),

    html.Div([
    html.Img(id='segmentation-img', width=100),
    html.Img(id='ColorSegmentation-img', width=500, style={'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)', 'margin':'15px', 'position':'absolete'}),
    html.Img(id='ColorHSVSegmentation-img', width=500, style={'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)', 'margin':'15px','position':'relative'}),
    html.Img(id='resized-img', width=500, style={'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)', 'margin':'15px'}),
    #html.Img(id='KmeanColorSegmentation-img', width=500),
    html.Div(id='KmeanColorSegmentation-img'),
            html.Div(id='color_range'),
            html.Div(id='container-button-basic'),
            html.Div([html.Button('Save', id='save-output', style={'display':'None'})]), #, Download(id="download")
            html.Br(),
            html.Div([
                        html.Button('Download image', id='SAVE', 
                            style={'display':'block'
                                    ,'position':'relative',
                                    'top': '45%','left': '45%',
                                    'font-size': '16px',
                                    'padding': '8px 12px',
                                    'border-radius': '4px',
                                    'text-align': 'center',
                                    'align':'center',
                                    'color':'black',
                                    'font-family':'Times New Roman',
                                    'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)',
                                    'textAlign':'center'})
                        ,Download(id="download")
                    ]),
            html.Br(),
            ]),#className="five columns", style={'height':'100', 'width':'100'}),
 
], style={'textAlign': 'center','background-color': 'rgb(59, 63, 71)','color': 'white', 'font-family':'Times New Roman','margin-left': '15%','margin-right': 'auto','width': '100%'})
    ], style={'textAlign': 'center','background-color': 'rgb(59, 63, 71)','color': 'white', 'font-family':'Times New Roman','align':'center','margin-top':0,'top':0,'margin':'None','max-width': '100%', 'overflow-x': 'hidden'})
########################################################################################################################################
########################################################################################################################################
# END OF MAIN HTML DIV
########################################################################################################################################
########################################################################################################################################

def parse_contents(contents):#, filename, date):
    return html.Div([
        DashCanvas(id='annot-canvas',
               lineWidth=5,
               image_content = contents,
               width=565,
               height=100,
               goButtonTitle='Segment'
               ),
    ]),

@app.callback([Output('output-image-upload', 'children'),Output('upload-image', 'style'),Output('upload-button', 'style')],
              [Input('upload-image', 'contents')])#,

def update_output_div(list_of_contents):#, list_of_names, list_of_dates):
    if list_of_contents is None:
        print('None triggerred')
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
        print('image triggerred')
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
              [Input('thresholdColor-functionsDropdown', 'value'),#,Input('upload-image', 'contents')]
              ])

def displaySliders(colorSpaceOption):
    #print(colorSpaceOption)
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

@app.callback(Output('output-container-range-slider', 'children'),
             [Input('red', 'value'),Input('green', 'value'),Input('blue', 'value')],
              prevent_initial_call=True,)

def update_slider(value, value2, value3):
    return html.Div([
            html.Button(value[0], id='submit-val', style={'background-color':'rgb(255, 92, 92)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
            html.Button(value[1], id='submit-val', style={'background-color':'rgb(255, 66, 66)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
            html.Button(value2[0], id='submit-val', style={'background-color':'rgb(208, 235, 89)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
            html.Button(value2[1], id='submit-val', style={'background-color':'rgb(16, 156, 25)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
            html.Button(value3[0], id='submit-val', style={'background-color':'rgb(71, 184, 196)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
            html.Button(value3[1], id='submit-val', style={'background-color':'rgb(0, 96, 122)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none'}),
        ])

@app.callback(Output('output-container-HSVrange-slider', 'children'),
             [Input('hue', 'value'),Input('saturation', 'value'),Input('val', 'value')],
              prevent_initial_call=True,)

def update_HSVslider(value, value2, value3):
    return html.Div([
            html.Button(value, id='submit-val', style={'background-image': 'linear-gradient(to right, #f6d365 0%, #f6d365 20%, #fda085 40%, #fc5603 60%, #f403fc 80%, #4503fc 100%)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none', 'padding-right':'20px','padding-left':'20px'}),
            html.Button(value2, id='submit-val', style={'background-image': 'linear-gradient(to right, #ffffff 0%, #9342f5 100%)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none','padding-right':'20px','padding-left':'20px'}),
            html.Button(value3, id='submit-val', style={'background-image': 'linear-gradient(to right, #000000 0%, #9342f5 100%)','display': 'inline-block','margin': '0px 0px','font-size': '16px','box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)','font-family':'Times New Roman','border':'none','color':'white','padding-right':'20px','padding-left':'20px'}),           
        ])

@app.callback(Output('ColorSegmentation-img', 'src'),
              [Input('upload-image', 'contents'),              
              Input('main-functionsDropdown', 'value'),#,Input('upload-image', 'contents')]
              Input('red', 'value'),Input('green', 'value'),Input('blue', 'value'),
              ]) 

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
              ]) 


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
                                            html.Img(src=array_to_data_url(img_as_ubyte(ex_img)),width =600,style={'box-shadow': '0 4px 12px 0 rgba(0, 0, 0, 1)', 'margin':'15px'})
                                            ]))
                return image_div
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


#######################################################################################################################

if __name__ == '__main__':
    app.run_server(debug=True)


