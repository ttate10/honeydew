from flask import Flask, render_template, jsonify, request
from flask.logging import default_handler
import logging.config
import plotly.graph_objects as go
import os
import json
import pandas as pd
import plotly.express as px
import re
from honeypot.logger import web_logger

app = Flask(__name__)

# Paths to the folders containing JSON files
LOGINS_DIR = './env/logins/'
CONNECTIONS_DIR = './env/connections/'
COMMAND_HISTORY_DIR = './env/command_history/'

def set_env_directory(directory):
    global LOGINS_DIR
    global CONNECTIONS_DIR
    global COMMAND_HISTORY_DIR
    LOGINS_DIR = os.path.join(directory, 'logins')
    CONNECTIONS_DIR = os.path.join(directory, 'connections')
    COMMAND_HISTORY_DIR = os.path.join(directory, 'command_history')

def load_json_files(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename)) as file:
                data.append(json.load(file))
    return data

@app.route('/')
def index():
    web_logger.info(f"{request.remote_addr} Accessed the index page.")
    return render_template('index.html')


@app.route('/logins')
def logins():
    web_logger.info(f"{request.remote_addr} Accessed the logins page.")
    logins_data = []
    
    # Regex pattern to match daily files
    pattern = re.compile(r'logins_(\d{4}-\d{2}-\d{2})\.json')

    # Load JSON files with specific pattern
    for filename in os.listdir(LOGINS_DIR):
        match = pattern.match(filename)
        if match:
            with open(os.path.join(LOGINS_DIR, filename)) as file:
                data = json.load(file)
                if isinstance(data, list):
                    logins_data.extend([item for item in data if isinstance(item, dict)])

    if not logins_data:
        return "No valid login data found.", 404

    # Convert to DataFrame
    df = pd.DataFrame(logins_data)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Set timestamp as the index for resampling
    df.set_index('timestamp', inplace=True)

    # Add a count column (if needed, for clarity)
    df['count'] = 1

    # Resample by day and sum the counts for overall logins
    daily_counts = df.resample('D').agg({'count': 'sum'}).reset_index()

    # Resample by day and sum the counts for each IP address
    ip_daily_counts = df.groupby(['ip']).resample('D').agg({'count': 'sum'}).reset_index()

    # Initialize the figure
    fig = go.Figure()

    # Add overall daily counts line
    fig.add_trace(go.Scatter(x=daily_counts['timestamp'], y=daily_counts['count'],
                             mode='lines', name='Total Daily Count'))

    # Add lines for each IP address
    for ip, group in ip_daily_counts.groupby('ip'):
        fig.add_trace(go.Scatter(x=group['timestamp'], y=group['count'],
                                 mode='lines', name=f'IP: {ip}'))

    # Add traces for successful and unsuccessful logins
    successful_logins = df[df['successfull_login'] == True].resample('D').agg({'count': 'sum'}).reset_index()
    unsuccessful_logins = df[df['successfull_login'] == False].resample('D').agg({'count': 'sum'}).reset_index()

    fig.add_trace(go.Scatter(x=successful_logins['timestamp'], y=successful_logins['count'],
                             mode='lines', line=dict(dash='dash'), name='Successful Logins',
                             marker_color='green'))

    fig.add_trace(go.Scatter(x=unsuccessful_logins['timestamp'], y=unsuccessful_logins['count'],
                             mode='lines', line=dict(dash='dot'), name='Unsuccessful Logins',
                             marker_color='red'))

    # Update layout
    fig.update_layout(
        title='Daily Login Count',
        xaxis_title='Date',
        yaxis_title='Count',
        legend_title='Legend'
    )

    # Convert plot to JSON
    graphJSON = fig.to_json()

    return render_template('graph.html', graphJSON=graphJSON)

@app.route('/connections/monthly')
def monthly_connections():
    web_logger.info(f"{request.remote_addr} Accessed the monthly connections page.")
    connections_data = []
    
    # Regex pattern to match daily files
    pattern = re.compile(r'connections_(\d{4}-\d{2}\.json')

    # Load JSON files with specific pattern
    for filename in os.listdir(CONNECTIONS_DIR):
        match = pattern.match(filename)
        if match:
            with open(os.path.join(CONNECTIONS_DIR, filename)) as file:
                data = json.load(file)
                if isinstance(data, list):
                    connections_data.extend([item for item in data if isinstance(item, dict)])

    if not connections_data:
        return "No valid connection data found.", 404

    # Convert to DataFrame
    df = pd.DataFrame(connections_data)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Set timestamp as the index for resampling
    df.set_index('timestamp', inplace=True)

    # Add a count column (if needed, for clarity)
    df['count'] = 1

    # Resample by day and sum the counts
    daily_counts = df.resample('D').agg({'count': 'sum'}).reset_index()
    # df['cumulative_count'] = df.groupby(['ip', 'port', 'timestamp']).cumcount() + 1

    # Create a Plotly line graph
    fig = px.line(daily_counts, x='timestamp', y='count',
                  title='Daily Connection Count',
                  labels={'count': 'Daily Count', 'timestamp': 'Date'})

    # Return the plot as HTML
    # Convert plot to JSON
    graphJSON = fig.to_json()

    return render_template('graph.html', graphJSON=graphJSON)

@app.route('/connections')
def connections():
    web_logger.info(f"{request.remote_addr} Accessed the connections page.")
    connections_data = []
    
    # Regex pattern to match daily files
    pattern = re.compile(r'connections_(\d{4}-\d{2}-\d{2})\.json')

    # Load JSON files with specific pattern
    for filename in os.listdir(CONNECTIONS_DIR):
        match = pattern.match(filename)
        if match:
            with open(os.path.join(CONNECTIONS_DIR, filename)) as file:
                data = json.load(file)
                if isinstance(data, list):
                    connections_data.extend([item for item in data if isinstance(item, dict)])

    if not connections_data:
        return "No valid connection data found.", 404

    # Convert to DataFrame
    df = pd.DataFrame(connections_data)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Set timestamp as the index for resampling
    df.set_index('timestamp', inplace=True)

    # Add a count column (if needed, for clarity)
    df['count'] = 1

    # Resample by day and sum the counts for overall connections
    daily_counts = df.resample('D').agg({'count': 'sum'}).reset_index()

    # Resample by day and sum the counts for each IP address
    ip_daily_counts = df.groupby(['ip']).resample('D').agg({'count': 'sum'}).reset_index()

    # Create a Plotly line graph
    fig = px.line(daily_counts, x='timestamp', y='count',
                  title='Daily Connection Count',
                  labels={'count': 'Daily Count', 'timestamp': 'Date'})

    # Add lines for each IP address
    fig.add_traces(px.line(ip_daily_counts, x='timestamp', y='count', color='ip').data)

    # Convert plot to JSON
    graphJSON = fig.to_json()

    return render_template('graph.html', graphJSON=graphJSON)

@app.route('/command_history')
def command_history():
    web_logger.info(f"{request.remote_addr} Accessed the command history page.")
    command_files = os.listdir(COMMAND_HISTORY_DIR)
    return render_template('command_history.html', files=command_files)

@app.route('/command_history/<filename>')
def command_history_file(filename):
    web_logger.info(f"{request.remote_addr} Accessed the command history file: {filename}.")
    filepath = os.path.join(COMMAND_HISTORY_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath) as file:
            data = json.load(file)
            df = pd.DataFrame(data)
            tableHTML = df.to_html(classes='table table-striped')
            return render_template('table.html', tableHTML=tableHTML)
    else:
        return "File not found", 404
