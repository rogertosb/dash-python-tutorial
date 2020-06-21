# Import dash and dependencies for reading vehicle sensor data
import dash
import dash_core_components as dcc
import dash_html_components as html

from pandas_datareader.data import DataReader
import time
from collections import deque
import plotly.graph_objs as go
import random

# Defines the app and its relevant datapoints, appends css and js from external links for the app


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]

external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']

app = dash.Dash('vehicle-data',

                external_scripts=external_js,

                external_stylesheets=external_css)

max_length = 50
times = deque(maxlen=max_length)
oil_temps = deque(maxlen=max_length)
intake_temps = deque(maxlen=max_length)
coolant_temps = deque(maxlen=max_length)
rpms = deque(maxlen=max_length)
speeds = deque(maxlen=max_length)
throttle_pos = deque(maxlen=max_length)

# assign all vars(datapoints) to a dictionary

data_dict = {
'Oil Temperature': oil_temps,
'Intake Temperature': intake_temps,
'Coolant Temperature': coolant_temps,
'Rounds Per Minute (RPMs)': rpms,
'Speed': speeds,
'Throttle Position': throttle_pos
}

# creates sample data within random but reasonable ranges for each datapoint

def update_obd_values(times, oil_temps, intake_temps, coolant_temps, rpms, speeds, throttle_pos):
  times.append(time.time())
  if len(times) == 1:
    oil_temps.append(random.randrange(180,230))
    intake_temps.append(random.randrange(95,115))
    coolant_temps.append(random.randrange(170, 220))
    rpms.append(random.randrange(1000, 9500))
    speeds.append(random.randrange(30, 140))
    throttle_pos.append(random.randrange(10, 90))
  else:
    for data_of_interest in [oil_temps, intake_temps, coolant_temps, rpms, speeds, throttle_pos]:
      data_of_interest.append(data_of_interest[-1]+data_of_interest[-1]*random.uniform(-0.0001, 0.0001))
  return times, oil_temps, intake_temps, coolant_temps, rpms, speeds, throttle_pos

  times, oil_temps, intake_temps, coolant_temps, rpms, speeds, throttle_pos = update_obd_values(times, oil_temps, intake_temps, coolant_temps, rpms, speeds, throttle_pos)

# App layout structure

#Sets header and style
app.layout = html.Div([
  html.Div([
    html.H2('Vehicle Data',
      style={'float': 'left',
      }),
    ]),
#Creates specifications for dropdown menu, allowing multiple options simultaneously
  dcc.Dropdown(id='vehicle-data-name',
    options=[{'label': s, 'value': s}
    for s in data_dict.keys()],
    value=['Coolant Temperature', 'Oil Temperature', 'Intake Temperature'],
    multi=True
    ),
    html.Div(children=html.Div(id='graphs'), className='row'),
    dcc.Interval(
      id='graph-update',
      interval=1000,
      n_intervals=0),
    ], className='container', style={'width': '98%', 'margin-left': 10, 'margin-right': 10, 'max-width': 50000})

# Sets specification sfor decorator input, output, and events
@app.callback(
  dash.dependencies.Output('graphs', 'children'),
  [dash.dependencies.Input('vehicle-data-name', 'value'),
  dash.dependencies.Input('graph-update', 'n_intervals')],
  )

# updating user input and setting the appropriate scaling to update automatically based on data size

def update_graph(data_names, n):
  graphs = []
  update_obd_values(times, oil_temps, intake_temps, coolant_temps, rpms, speeds, throttle_pos)

  if len(data_names)> 2:
    class_choice = 'col s12 m6 l4'
  elif len(data_names) == 2:
    class_choice = 'col s12 m6 l6'
  else:
    class_choice = 'col s12'


  for data_name in data_names:

    data = go.Scatter(
      x=list(times),
      y=list(data_dict[data_name]),
      name='Scatter',
      fill='tozeroy',
      fillcolor='#6897bb'
      )

  graphs.append(html.Div(dcc.Graph(
    id=data_name,
    animate=True,
    figure={'data': [data], 'layout' : go.Layout(
      xaxis=dict(range=[min(times), max(times)]),
      yaxis=dict(range=[min(data_dict[data_name]), max(data_dict[data_name])]),
      margin={'l':50, 'r': 1, 't': 45, 'b': 1},
      title= '{}'.format(data_name))}
     ), className= class_choice))
  return graphs


#runs app

if __name__ == '__main__':
  app.run_server(debug=True)
