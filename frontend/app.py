import dash
from dash import html, dcc, Input, Output, State
import requests

# Docker internal network routing
BACKEND_URL = "http://backend_api:8000"

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Crate Digger Studio", style={'color': '#38bdf8', 'fontFamily': 'sans-serif'}),
    
    html.Div([
        dcc.Textarea(id='link-input', placeholder='Paste URLs here...', style={'width': '100%', 'height': '100px'}),
        html.Button("Add to Queue", id='btn-add', style={'padding': '10px', 'marginTop': '10px', 'cursor': 'pointer'}),
        html.Div(id='add-status', style={'color': '#10b981', 'marginTop': '10px', 'fontWeight': 'bold'})
    ], style={'maxWidth': '600px', 'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#f1f5f9', 'borderRadius': '8px'}),

    html.H3("Live Queue (Fetched from API)"),
    html.Button("Refresh Queue", id='btn-refresh', style={'marginBottom': '10px'}),
    html.Div(id='queue-table'),
])

@app.callback(
    Output('add-status', 'children'),
    Input('btn-add', 'n_clicks'),
    State('link-input', 'value'),
    prevent_initial_call=True
)
def add_to_backend(n, text):
    if not text: return ""
    links = [l.strip() for l in text.split('\n') if l.strip().startswith('http')]
    try:
        # The frontend DOES NO WORK. It just asks the backend to do it.
        res = requests.post(f"{BACKEND_URL}/api/ripper/add", json={"links": links})
        return res.json().get("message", "Success")
    except Exception as e:
        return f"API Error: {e}"

@app.callback(
    Output('queue-table', 'children'),
    Input('btn-refresh', 'n_clicks')
)
def fetch_queue(n):
    try:
        res = requests.get(f"{BACKEND_URL}/api/ripper/queue")
        data = res.json()
        if not data: return "Queue is empty."
        
        rows = [html.Tr([html.Td(d['track_name']), html.Td(d['status'])]) for d in data]
        return html.Table([
            html.Thead(html.Tr([html.Th("Track"), html.Th("Status")])),
            html.Tbody(rows)
        ], style={'width': '100%', 'textAlign': 'left'})
    except Exception as e:
        return f"Could not connect to backend. Is it running? Error: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)