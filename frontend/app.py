import dash
from dash import html, dcc, Input, Output, State
from dash_iconify import DashIconify
import requests
from flask import send_from_directory
import os
from datetime import datetime

BACKEND_URL = "http://composer_backend:8001"
OUTPUT_DIR = '/app/shared_outputs'

app = dash.Dash(__name__, title="AI Beat Composer")
server = app.server

@server.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

# Custom tab styles to match your dark theme
TAB_STYLE = {'backgroundColor': '#1e293b', 'color': '#94a3b8', 'border': 'none', 'borderTop': '2px solid transparent', 'padding': '15px', 'fontWeight': 'bold', 'cursor': 'pointer'}
TAB_SELECTED_STYLE = {'backgroundColor': '#0f172a', 'color': '#38bdf8', 'border': 'none', 'borderTop': '2px solid #38bdf8', 'padding': '15px', 'fontWeight': 'bold', 'cursor': 'default'}

app.layout = html.Div(className="studio-container", children=[
    
    html.Div(className="header", children=[
        html.H1([DashIconify(icon="mdi:waveform", width=40, style={'verticalAlign': 'middle', 'marginRight': '10px'}), "AI Composer Studio"]),
        html.P("Dual-Engine Beat Generation. Powered by Python & PyTorch.", style={'color': '#94a3b8'})
    ]),

    dcc.Tabs(id="app-tabs", value='tab-studio', children=[
        
        # --- TAB 1: THE STUDIO ---
        dcc.Tab(label='🎛️ The Studio', value='tab-studio', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE, children=[
            html.Div(style={'marginTop': '30px'}, children=[
                html.Div(className="panel", children=[
                    html.H2([DashIconify(icon="mdi:brain", width=24), " Text-to-Music Neural Engine"], className="panel-title text-purple"),
                    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
                        html.Div(style={'flex': '3'}, children=[
                            html.Label("Prompt (Describe the sound)", className="input-label"),
                            dcc.Input(id="ai-prompt", type="text", className="custom-input", placeholder="e.g., 120 bpm lo-fi hip hop drum loop")
                        ]),
                        html.Div(style={'flex': '1'}, children=[
                            html.Label("Duration (Secs)", className="input-label"),
                            dcc.Input(id="ai-duration", type="number", className="custom-input", value=10, min=5, max=30)
                        ])
                    ]),
                    html.Button([DashIconify(icon="mdi:creation", width=20), " Synthesize Audio (.WAV)"], id="btn-ai", className="btn-generate btn-ai", n_clicks=0),
                    dcc.Loading(type="circle", color="#a855f7", style={'marginTop': '40px'}, children=[html.Div(id="ai-output")])
                ]),
                html.Br(),
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
                    dcc.Loading(type="circle", color="#2dd4bf", style={'marginTop': '40px'}, children=[html.Div(id="math-output")])
                ])
            ])
        ]),

        # --- TAB 2: THE VAULT ---
        dcc.Tab(label='📁 The Vault', value='tab-vault', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE, children=[
            html.Div(className="panel", style={'marginTop': '30px'}, children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '20px'}, children=[
                    html.H2([DashIconify(icon="mdi:folder-music", width=24), " Your Generated Files"], className="panel-title", style={'border': 'none', 'margin': '0', 'padding': '0'}),
                    html.Button([DashIconify(icon="mdi:refresh", width=18), " Refresh"], id="btn-refresh-vault", style={'backgroundColor': '#334155', 'color': 'white', 'border': 'none', 'padding': '8px 16px', 'borderRadius': '6px', 'cursor': 'pointer'})
                ]),
                html.Div(id="vault-gallery")
            ])
        ])
    ])
])

# --- CALLBACKS ---

@app.callback(
    Output("vault-gallery", "children"),
    Input("btn-refresh-vault", "n_clicks"),
    Input("app-tabs", "value")
)
def load_vault(n_clicks, tab):
    if tab != 'tab-vault':
        return dash.no_update
    
    try:
        files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.wav') or f.endswith('.mid')]
        if not files:
            return html.Div("Your vault is empty. Go generate some beats!", style={'color': '#94a3b8', 'textAlign': 'center', 'padding': '40px'})
        
        # Sort files by newest first
        files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
        
        file_cards = []
        for file in files:
            file_path = os.path.join(OUTPUT_DIR, file)
            creation_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
            
            # If it's a WAV, add an audio player
            player = html.Audio(src=f"/downloads/{file}", controls=True, style={'width': '100%', 'marginTop': '10px'}) if file.endswith('.wav') else html.Div("MIDI File (No browser preview)", style={'color': '#64748b', 'fontSize': '12px', 'marginTop': '10px'})
            
            card = html.Div(style={'backgroundColor': '#0f172a', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px', 'border': '1px solid #334155'}, children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between'}, children=[
                    html.Strong(file, style={'color': '#38bdf8', 'wordBreak': 'break-all'}),
                    html.A([DashIconify(icon="mdi:download"), " Download"], href=f"/downloads/{file}", style={'color': '#10b981', 'textDecoration': 'none', 'fontWeight': 'bold', 'whiteSpace': 'nowrap', 'marginLeft': '15px'})
                ]),
                html.Div(f"Generated: {creation_time} | Size: {size_mb} MB", style={'color': '#64748b', 'fontSize': '12px', 'marginTop': '5px'}),
                player
            ])
            file_cards.append(card)
            
        return html.Div(file_cards)
    except Exception as e:
        return html.Div(f"Error loading vault: {str(e)}", style={'color': '#ef4444'})

# (Keep your existing generate_ai and generate_math callbacks exactly as they are down here)
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