import dash
import pandas as pd
from dash import html, dcc, callback, Output, Input
import dash_ag_grid as dag
import src.utils as utils
from pathlib import Path
from urllib.parse import quote

ROOT_DIR = Path(__file__).resolve().parents[2]
data_folder = f"{ROOT_DIR}/data/"

def get_display_data():
    df = utils.get_asset("reality_cast.csv")
    insta = utils.get_asset("insta_latest.csv")

    merged = df.merge(insta[["name", "insta_username"]], on="name", how="left")
    merged["IG Username"] = merged["insta_username"].apply(
            lambda u: f"[{u}](https://www.instagram.com/{quote(u, safe='')}/)" if pd.notna(u) and u else "")
    merged = merged.rename(columns={"name": "Contestant", "show": "Show", "season": "Season"})
    return merged[["Contestant", "Show", "Season", "IG Username"]]

ERROR_MESSAGE = "Oops, something went wrong loading the data. Please try again later."

@callback(
    Output("season-filter", "options"),
    Output("error-banner", "children", allow_duplicate=True),
    Input("show-filter", "value"),
    prevent_initial_call=True,
)
def update_season_options(selected_shows):
    try:
        cast_df = utils.get_asset("reality_cast.csv")
        if selected_shows:
            cast_df = cast_df[cast_df["show"].isin(selected_shows)]
        seasons = sorted(cast_df["season"].dropna().unique().astype(int))
        return [{"label": f"Season {s}", "value": s} for s in seasons], ""
    except Exception as e:
        _logger.error("update_season_options failed: %s", e)
        return [], ERROR_MESSAGE

@callback(
    Output("my-table", "rowData"),
    Output("error-banner", "children", allow_duplicate=True),
    Input("show-filter", "value"),
    Input("season-filter", "value"),
    Input("contestant-search", "value"),
    prevent_initial_call=True,
)
def update_table(selected_shows, selected_seasons, search_text):
    try:
        filtered_df = get_display_data()

        if selected_shows:
            filtered_df = filtered_df[filtered_df["Show"].isin(selected_shows)]

        if selected_seasons:
            filtered_df = filtered_df[filtered_df["Season"].isin(selected_seasons)]

        if search_text:
            search_text = utils.sanitize_search_input(search_text)
            filtered_df = filtered_df[filtered_df["Contestant"]
                                    .str.contains(search_text, case=False, na=False, regex=False)]
        return filtered_df.to_dict("records"), ""
    except Exception as e:
        _logger.error("update_table failed: %s", e)
        return []

@callback(
    Output("person-details", "children"),
    Output("error-banner", "children", allow_duplicate=True),
    Input("my-table", "selectedRows"),
    prevent_initial_call=True,
)
def show_person_details(selected_rows):
    if not selected_rows:
        return "Select a row to see details", ""
    try:
        row = selected_rows[0]
        name = row.get("Contestant", "Unknown")

        df = utils.get_asset("reality_cast.csv")
        filtered_df = df[df['name'] == name][["hometown", "state", "job", "show"]].fillna("unknown")

        if filtered_df.empty:
            return html.Div([html.H3(row.get("Contestant")), html.P("No details found.")]), ""

        hometown = filtered_df.iloc[0]["hometown"]
        state = filtered_df.iloc[0]["state"]
        job = filtered_df.iloc[0]["job"]
        show = filtered_df.iloc[0]["show"]

        return html.Div([
            html.H3(row.get("Contestant")),
            html.P(f"Rookie Season: {show}"),
            html.P(f"Hometown: {hometown}, {state}"),
            html.P(f"Civilian Job: {job}"),
        ]), ""
    except Exception as e:
        _logger.error("show_person_details failed: %s", e)


def get_cast_filter_options():
    """Load show and season filter options from reality_cast.csv."""
    cast_df = utils.get_asset("reality_cast.csv")
    
    # Exclude rows where 'show' is a bare number (data quality issue)
    valid_shows = cast_df[~cast_df["show"].astype(str).str.match(r"^\d+$")]["show"]
    shows = sorted(valid_shows.dropna().unique())
    seasons = sorted(cast_df["season"].dropna().unique().astype(int))
    return shows, seasons

_filter_shows, _filter_seasons = get_cast_filter_options()

_logger = utils.get_logger(__name__)

dash.register_page(__name__, path='/')
try:
    main_grid_df = get_display_data().to_dict("records")
    _logger.info("Loaded %d rows for main grid", len(main_grid_df))
except Exception as e:
    _logger.error("Could not load display data: %s", e)
    main_grid_df = []


### Page HTML
layout = html.Div([

    html.Div(
        id="error-banner",
        style={
            "display": "block",
            "color": "#8E6E75",
            "backgroundColor": "#FAE0E4",
            "padding": "10px 20px",
            "textAlign": "center",
            "fontStyle": "italic",
        }
    ),

    html.Div([

        ########### LEFT: FILTERS
        html.Div([
            html.H4("Filters", style={"color": "#8E6E75", "marginTop": "0"}),

            # --- SHOW FILTER ---
            html.Label("Show", style={"fontWeight": "bold", "color": "#8E6E75", "fontSize": "13px"}),
            dcc.Dropdown(
                id="show-filter",
                options=[{"label": s, "value": s} for s in _filter_shows],
                placeholder="Select Show",
                multi=True, # Allows selecting multiple shows at once
                style={"marginBottom": "20px"}
            ),

            # --- SEASON FILTER ---
            html.Label("Season", style={"fontWeight": "bold", "color": "#8E6E75", "fontSize": "13px"}),
            dcc.Dropdown(
                id="season-filter",
                options=[{"label": f"Season {s}", "value": s} for s in _filter_seasons],
                placeholder="Select Season",
                multi=True,
                style={"marginBottom": "20px"}
            ),
            # --- CONTESTANT SEARCH ---
            html.Label("Contestant", style={"fontWeight": "bold", "color": "#8E6E75", "fontSize": "13px"}),
            dcc.Input(
                id="contestant-search",
                placeholder="Search contestant...",
                debounce=True,
                style={"marginBottom": "20px", "width": "100%"}
            ),


        # Add more filters here easily!
        ], style={
                "width": "250px",  # Fixed width for sidebar
                "backgroundColor": "white",
                "padding": "25px",
                "borderRight": "1px solid #E5D1D5",
                "display": "flex",
                "flexDirection": "column",
                "height": "90%"
            }
        ),
        ##### END OF LEFT


        ### MIDDLE: TABLE
        dag.AgGrid(
            id="my-table",
            rowData=main_grid_df,      # The data
            columnDefs=[
                {"field": "Contestant"},
                {"field": "Show"},
                {"field": "Season"},

                {
                    "field": "IG Username",
                    "cellRenderer": "markdown",
                    "cellRendererParams": {"linkTarget": "_blank"},
                },
                
            ],

            columnSize="sizeToFit",
            columnSizeOptions={
                "defaultMinWidth": 100,
                "columnLimits": [{"key": "Contestant", "minWidth": 150}],
            },
            dashGridOptions={
                "pagination": True,
                "responsiveSizeToFit": True, # This is the magic toggle
                "rowSelection": "single",
                "cacheBlockSize": 100, 
                "maxBlocksInCache": 10,
            }, style={"height": "90vh", "width": "95%"}
        ),

    # RIGHT GRID
    ], className="table-panel", style={
                "display": "flex",           # Enable Flexbox
                "justifyContent": "center",  # Center children horizontally within the 50% width
                "alignItems": "center",      # Center children vertically
                "height": "calc(100vh - 80px)",
                "width": "70%",              # Occupy exactly half the container width
                "backgroundColor": "#FAF3F4",
                "boxSizing": "border-box",   # Ensures padding doesn't push width past 50%
                "float": "left"              # Optional: Aligns the div to the left side
            },


    ),
    html.Div(
            id="person-details",
            className="details-panel",
            style={
                "flex": 1,
                "border": "1px solid #ddd",
                "padding": "10px",
                "borderRadius": "4px",
                "minWidth": "100px",
            },
            children="Select a row to see details",
    ),
], style={"margin": "0", "padding": "0", "display": "flex", "gap": "24px", "width": "100%"},
)
