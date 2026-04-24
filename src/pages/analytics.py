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
            "display": "none",
            "color": "#8E6E75",
            "backgroundColor": "#FAE0E4",
            "padding": "10px 20px",
            "textAlign": "center",
            "fontStyle": "italic",
        }
    ),

    # TOP: FILTER BAR
    html.Div([
        html.Div([
            html.Label("Contestant", style={"fontWeight": "bold", "color": "#8E6E75", "fontSize": "13px", "marginBottom": "4px"}),
            dcc.Input(
                id="contestant-search",
                placeholder="Search contestant...",
                debounce=True,
                style={"width": "100%"}
            ),
        ], style={"flex": "1"}),

        html.Div([
            html.Label("Show", style={"fontWeight": "bold", "color": "#8E6E75", "fontSize": "13px", "marginBottom": "4px"}),
            dcc.Dropdown(
                id="show-filter",
                options=[{"label": s, "value": s} for s in _filter_shows],
                placeholder="Select Show",
                multi=True,
            ),
        ], style={"flex": "2"}),

        html.Div([
            html.Label("Season", style={"fontWeight": "bold", "color": "#8E6E75", "fontSize": "13px", "marginBottom": "4px"}),
            dcc.Dropdown(
                id="season-filter",
                options=[{"label": f"Season {s}", "value": s} for s in _filter_seasons],
                placeholder="Select Season",
                multi=True,
            ),
        ], style={"flex": "1"}),

    ], className="panel filter-bar", style={
        "display": "flex",
        "flexDirection": "row",
        "gap": "16px",
        "margin": "16px 16px 0 16px",
        "alignItems": "flex-end",
    }),

    # 2-column CSS grid: table | details
    html.Div([

        # LEFT: TABLE
        html.Div(className="panel", style={"padding": "0", "overflow": "hidden", "minHeight": "0"}, children=[
            dag.AgGrid(
                id="my-table",
                rowData=main_grid_df,
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
                    "responsiveSizeToFit": True,
                    "rowSelection": "single",
                    "cacheBlockSize": 100,
                    "maxBlocksInCache": 10,
                },
                style={"height": "100%", "width": "100%"}
            ),
        ]),

        # RIGHT: DETAILS
        html.Div(
            id="person-details",
            className="details-panel panel",
            children="Select a row to see details",
        ),

    ], className="content-grid", style={
        "display": "grid",
        "gridTemplateColumns": "1fr 260px",
        "gap": "16px",
        "height": "calc(100vh - 180px)",
        "padding": "16px",
        "backgroundColor": "#FAF3F4",
        "boxSizing": "border-box",
    }),

], style={"margin": "0", "padding": "0"})
