import dash
import pandas as pd
import os
from dash import Dash, html, dcc
from pathlib import Path
import src.config as config

src_path = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = Path(__file__).parent

app = Dash(__name__,
           title="Reality TV Data",
           use_pages=True,
           meta_tags=[{'name': 'viewport',
                        'content': 'width=device-width, '
                        'initial-scale=1.0, '
                        'maximum-scale=1.2, minimum-scale=0.5,'}]
                    )
server = app.server


# Updated styles for a compact, centered look
tab_style = {
    #"padding": "0 20px",        # Horizontal padding creates the "breathing room"
    "lineHeight": "40px",
    "border": "none",
    "backgroundColor": "transparent",
    "color": "white",
    "cursor": "pointer",
    "flex": "0 1 auto",         # IMPORTANT: Prevents stretching, allows content-based width
    "minWidth": "fit-content",  # Ensures the tab is at least as wide as the word
    "whiteSpace": "nowrap"      # Prevents words from wrapping to a second line
}

tab_selected_style = {
    **tab_style,
    "fontWeight": "bold",
    "borderBottom": "3px solid white"
}
app.layout = html.Div([
html.Div(
        style={
            "backgroundColor": "#EDD9DC",
            "display": "flex",
            "flexDirection": "row",
            "alignItems": "center",
            "justifyContent": "center",
            "padding": "0 20px",
            "height": "60px",
            "borderRadius": "4px",
            "margin": "12px 16px 0 16px",
        },
        children=[
    html.H1('Reality TV Data',
            style={
                "color": "#000000",
                "margin": "0",
                "fontSize": "28px",
                "fontWeight": "600",
                "letterSpacing": "2px"
            }),
  
        ]),

    # This component renders the content of the current page
    dash.page_container
])

if __name__ == '__main__':
    cfg = config.get_config()
    app.run(host='127.0.0.1', port=8050, debug=cfg.DEBUG)