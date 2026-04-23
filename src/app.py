import dash
import pandas as pd
import os
from dash import Dash, html, dcc
from pathlib import Path
import src.config as config

src_path = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = Path(__file__).parent

app = Dash(__name__,
           use_pages=True,
           meta_tags=[{'name': 'viewport',
                        'content': 'width=device-width, '
                        'initial-scale=1.0, '
                        'maximum-scale=1.2, minimum-scale=0.5,'}]
                    )
server = app.server


# Updated styles for a compact, centered look
tab_style = {
    "padding": "0 20px",        # Horizontal padding creates the "breathing room"
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
            "backgroundColor": "#D8A7B1",  # Your muted pink background
            "display": "flex",             # Puts children side-by-side
            "flexDirection": "row",
            "alignItems": "center",        # Vertically aligns title and tabs
            "padding": "0 20px",           # Horizontal padding
            "height": "60px"               # Fixed height for a sleek bar
        },
        children=[
    html.H1('Reality Stats',
            style={
                "color": "white",
                "margin": "0",
                "marginRight": "40px",  # Space between title and tabs
                "fontFamily": "sans-serif",
                "fontSize": "24px"  # Slightly smaller to fit the bar
            }),
  
        ]),

    # This component renders the content of the current page
    dash.page_container
])

if __name__ == '__main__':
    cfg = config.get_config()
    app.run(host='0.0.0.0', port=8050, debug=cfg.DEBUG)