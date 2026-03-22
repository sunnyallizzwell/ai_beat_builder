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

# Custom tab styles
TAB_STYLE = {'backgroundColor': 'var(--tab-bg)', 'color': 'var(--text-muted)', 'border': 'none', 'borderBottom': '3px solid transparent', 'padding': '15px 25px', 'fontWeight': 'bold', 'cursor': 'pointer', 'transition': 'all 0.2s'}
TAB_SELECTED_STYLE = {'backgroundColor': 'var(--bg-panel)', 'color': 'var(--text-main)', 'border': 'none', 'borderBottom': '3px solid var(--accent-ai)', 'padding': '15px 25px', 'fontWeight': 'bold', 'cursor': 'default'}

app.layout = html.Div(className="studio-container", children=[
    
    html.Div(className="header", children=[
        html.H1([DashIconify(icon="mdi:waveform", width=46, style={'verticalAlign': 'middle', 'marginRight': '12px', 'color': '#f8fafc'}), "AI Composer Studio"]),
        html.P("Dual-Engine Beat Generation. Powered by Python & PyTorch.", style={'fontSize': '1.1rem'})
    ]),

    dcc.Tabs(id="app-tabs", value='tab-studio', style={'display': 'flex', 'justifyContent': 'center', 'borderBottom': '1px solid var(--border-color)'}, children=[
        
        # --- TAB 1: THE STUDIO ---
        dcc.Tab(label='🎛️ The Studio', value='tab-studio', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE, children=[
            
            # THE NEW DESKTOP GRID CONTAINER
            html.Div(className="engines-grid", children=[
                
                # PANEL 1: AI ENGINE
                html.Div(className="panel", children=[
                    html.H2([DashIconify(icon="mdi:brain", width=28, style={'marginRight':'10px'}), "Text-to-Music Neural Engine"], className="panel-title text-purple"),
                    
                    html.Div(className="input-row", children=[
                        html.Div(className="input-group wide", children=[
                            html.Label("Prompt (Describe the sound)", className="input-label"),
                            dcc.Input(id="ai-prompt", type="text", placeholder="e.g., 128 BPM big room house drop, punchy kick...")
                        ]),
                        html.Div(className="input-group", children=[
                            html.Label("Duration (Secs)", className="input-label"),
                            dcc.Input(id="ai-duration", type="number", value=10, min=5, max=30)
                        ])
                    ]),
                        # NEW SINGLE CHECKBOX FOR CONTINUATION
                    html.Div(style={'marginBottom': '20px', 'backgroundColor': '#0f172a', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #334155'}, children=[
                        dcc.Checklist(
                            id="ai-extend-track",
                            options=[
                                {'label': ' DJ Mix Mode: Seamlessly extend to a full 3-minute song (Takes longer to generate)', 'value': 'extend'}
                            ],
                            value=[], # Empty list means it is UNCHECKED by default
                            inputStyle={'marginRight': '12px', 'transform': 'scale(1.4)', 'accentColor': '#a855f7', 'cursor': 'pointer'},
                            labelStyle={'cursor': 'pointer', 'fontWeight': 'bold', 'color': '#38bdf8', 'display': 'flex', 'alignItems': 'center'}
                        )
                    ]),
                    
                    html.Button([DashIconify(icon="mdi:creation", width=22), " Synthesize Audio (.WAV)"], id="btn-ai", className="btn-generate btn-ai", n_clicks=0),
                    dcc.Loading(type="circle", color="#a855f7", style={'marginTop': '40px'}, children=[html.Div(id="ai-output")])
                ]),
                # PANEL 2: MATH ENGINE
                html.Div(className="panel", children=[
                    html.H2([DashIconify(icon="mdi:math-compass", width=28, style={'marginRight':'10px'}), "Algorithmic Grid Sequencer"], className="panel-title text-teal"),
                    
                    html.Div(className="input-row", children=[
                        html.Div(className="input-group", children=[
                            html.Label("Target BPM", className="input-label"),
                            dcc.Input(id="math-bpm", type="number", value=128)
                        ]),
                        html.Div(className="input-group", children=[
                            html.Label("Loop Length (Bars)", className="input-label"),
                            dcc.Input(id="math-bars", type="number", value=4)
                        ])
                    ]),
                    
                    html.Button([DashIconify(icon="mdi:calculator-variant", width=22), " Calculate Pattern (.MID)"], id="btn-math", className="btn-generate btn-math", n_clicks=0),
                    dcc.Loading(type="circle", color="#2dd4bf", style={'marginTop': '40px'}, children=[html.Div(id="math-output")])
                ])
                
            ])
        ]),

        # --- TAB 2: THE VAULT ---
        dcc.Tab(label='📁 The Vault', value='tab-vault', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE, children=[
            html.Div(className="panel", style={'marginTop': '2rem'}, children=[
                html.Div(className="vault-controls", children=[
                    html.H2([DashIconify(icon="mdi:folder-music", width=28, style={'marginRight':'10px'}), "Your Generated Files"], className="panel-title", style={'border': 'none', 'margin': '0', 'padding': '0'}),
                    html.Button([DashIconify(icon="mdi:refresh", width=20), " Refresh"], id="btn-refresh-vault", style={'backgroundColor': '#334155', 'color': 'white', 'border': 'none', 'padding': '10px 20px', 'borderRadius': '8px', 'cursor': 'pointer', 'fontWeight': 'bold'})
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
    State("ai-extend-track", "value"), # GET THE CHECKBOX STATE
    prevent_initial_call=True
)
def generate_ai(n_clicks, prompt, duration, extend_val):
    if not prompt: return html.Div("Please enter a prompt.", style={'color': '#ef4444', 'marginTop': '15px'})
    
    # If the checkbox is checked, 'extend' will be in the list
    is_extended = 'extend' in extend_val
    
    try:
        # Pass the boolean to the backend. Timeout increased to 20 mins to allow for heavy Continuation processing!
        res = requests.post(f"{BACKEND_URL}/api/ai/generate", json={"prompt": prompt, "duration": duration, "extend_track": is_extended}, timeout=1200)
        data = res.json()
        if data.get("status") == "success":
            filename = data.get("file")
            return html.Div(className="success-box", style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': '#1e293b', 'borderRadius': '8px'}, children=[
                html.Div("✅ Track Synthesized Successfully!", style={'color': '#a855f7', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.Audio(src=f"/downloads/{filename}", controls=True, style={'width': '100%'}),
                html.Br(),
                html.A([DashIconify(icon="mdi:download"), f" Download File"], href=f"/downloads/{filename}", style={'display': 'inline-block', 'marginTop': '10px', 'color': '#38bdf8', 'textDecoration': 'none', 'fontWeight': 'bold'})
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