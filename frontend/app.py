import dash
from dash import html, dcc, Input, Output, State
from dash_iconify import DashIconify
import requests
from flask import send_from_directory
import os

# Internal Docker Network routing to the backend
BACKEND_URL = "http://composer_backend:8001"
OUTPUT_DIR = '/app/shared_outputs'

app = dash.Dash(__name__, title="AI Beat Composer")
server = app.server

# Allow the frontend to directly serve the .wav and .mid files
@server.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

app.layout = html.Div(className="studio-container", children=[
    
    html.Div(className="header", children=[
        html.H1([DashIconify(icon="mdi:waveform", width=40, style={'verticalAlign': 'middle', 'marginRight': '10px'}), "AI Composer Studio"]),
        html.P("Dual-Engine Beat Generation. Powered by Python & PyTorch.", style={'color': '#94a3b8'})
    ]),

    # --- PANEL 1: AI NEURAL ENGINE ---
    html.Div(className="panel", children=[
        html.H2([DashIconify(icon="mdi:brain", width=24), " Text-to-Music Neural Engine"], className="panel-title text-purple"),
        
        html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
            html.Div(style={'flex': '3'}, children=[
                html.Label("Prompt (Describe the sound)", className="input-label"),
                dcc.Input(id="ai-prompt", type="text", className="custom-input", placeholder="e.g., 120 bpm lo-fi hip hop drum loop with vinyl crackle")
            ]),
            html.Div(style={'flex': '1'}, children=[
                html.Label("Duration (Secs)", className="input-label"),
                dcc.Input(id="ai-duration", type="number", className="custom-input", value=10, min=5, max=30)
            ])
        ]),

        html.Button([DashIconify(icon="mdi:creation", width=20), " Synthesize Audio (.WAV)"], id="btn-ai", className="btn-generate btn-ai", n_clicks=0),
        
        # Wrapped in a loading spinner for the 2-minute wait time
        dcc.Loading(type="circle", color="#a855f7", style={'marginTop': '40px'}, children=[
            html.Div(id="ai-output")
        ])
    ]),

    # --- PANEL 2: ALGORITHMIC MATH ENGINE ---
    html.Div(className="panel", children=[
        html.H2([DashIconify(icon="mdi:math-compass", width=24), " Algorithmic Grid Sequencer"], className="panel-title text-teal"),
        
        html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
            html.Div(style={'flex': '1'}, children=[
                html.Label("Target BPM", className="input-label"),
                dcc.Input(id="math-bpm", type="number", className="custom-input", value=128)
            ]),
            html.Div(style={'flex': '1'}, children=[
                html.Label("Loop Length (Bars)", className="input-label"),
                dcc.Input(id="math-bars", type="number", className="custom-input", value=4)
            ])
        ]),

        html.Button([DashIconify(icon="mdi:calculator-variant", width=20), " Calculate Pattern (.MID)"], id="btn-math", className="btn-generate btn-math", n_clicks=0),
        
        dcc.Loading(type="circle", color="#2dd4bf", style={'marginTop': '40px'}, children=[
            html.Div(id="math-output")
        ])
    ])
])

# --- CALLBACKS ---

@app.callback(
    Output("ai-output", "children"),
    Input("btn-ai", "n_clicks"),
    State("ai-prompt", "value"),
    State("ai-duration", "value"),
    prevent_initial_call=True
)
def generate_ai(n_clicks, prompt, duration):
    if not prompt: return html.Div("Please enter a prompt.", style={'color': '#ef4444', 'marginTop': '15px'})
    
    try:
        res = requests.post(f"{BACKEND_URL}/api/ai/generate", json={"prompt": prompt, "duration": duration}, timeout=300)
        data = res.json()
        
        if data.get("status") == "success":
            filename = data.get("file")
            return html.Div(className="success-box", children=[
                html.Audio(src=f"/downloads/{filename}", controls=True),
                html.Br(),
                html.A([DashIconify(icon="mdi:download"), f" Download {filename}"], href=f"/downloads/{filename}", className="download-link")
            ])
        else:
            return html.Div(f"Error: {data.get('message')}", style={'color': '#ef4444', 'marginTop': '15px'})
    except Exception as e:
        return html.Div(f"Connection Failed: {str(e)}", style={'color': '#ef4444', 'marginTop': '15px'})

@app.callback(
    Output("math-output", "children"),
    Input("btn-math", "n_clicks"),
    State("math-bpm", "value"),
    State("math-bars", "value"),
    prevent_initial_call=True
)
def generate_math(n_clicks, bpm, bars):
    try:
        res = requests.post(f"{BACKEND_URL}/api/math/generate", json={"bpm": float(bpm), "bars": int(bars)}, timeout=10)
        data = res.json()
        
        if data.get("status") == "success":
            filename = data.get("file")
            return html.Div(className="success-box", style={'borderColor': '#2dd4bf', 'backgroundColor': 'rgba(45, 212, 191, 0.1)'}, children=[
                html.Div("✅ Mathematical pattern calculated successfully!", style={'color': '#2dd4bf', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.A([DashIconify(icon="mdi:download"), f" Download {filename}"], href=f"/downloads/{filename}", className="download-link", style={'color': '#2dd4bf'})
            ])
        else:
            return html.Div("Calculation error.", style={'color': '#ef4444', 'marginTop': '15px'})
    except Exception as e:
        return html.Div(f"Connection Failed: {str(e)}", style={'color': '#ef4444', 'marginTop': '15px'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)