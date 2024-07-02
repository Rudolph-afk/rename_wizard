# import io
import re
import dash
from datetime import date
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import (
    dcc,
    html,
    callback,
    Input,
    Output,
    State,
    MATCH
)

app = dash.Dash(
    __name__,
    update_title="Loading...",
    url_base_pathname="/rename/",
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://unpkg.com/@mantine/dates@7/styles.css"]
    )

server = app.server

app.layout = dmc.MantineProvider(
    dbc.Container([
        dbc.Row([
            html.A(
                html.Img(
                    src="assets/airu_logo.jpg",
                    height="280px",
                    width="400px"
                ),
                href="#"
            ),
            # html.H1("File Renaming", style={'textAlign': 'center'}),
        ]),
        html.H2("Rename files for neut and luminex web application"),
        dbc.Row([
            dmc.SegmentedControl(
                id="assay-options",
                value="neut",
                data=[
                    {"value": "neut", "label": "NeutAssay"},
                    {"value": "luminex", "label": "LuminexAssay"},
                ],
                mb=10,
            )
        ]),
        dbc.Row([
            dcc.Upload(
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                multiple=True,
                id="files-input",
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px 0px 10px 0px'
                },
            )
        ]), # Choose limunex or neut + Upload button
        dbc.Row([
            dbc.Button(
                "Reset",
                type="reset",
                outline=True,
                color="dark",
                href="/rename/",
                external_link=True
            )
        ],
        justify="end"
        ),
        dbc.Row([
            dbc.Placeholder(color="primary", size="xl", className="me-1 mt-1 w-100"),
            dbc.Placeholder(color="secondary", size="lg", className="me-1 mt-1 w-100"),
            dbc.Placeholder(color="success", size="lg", className="me-1 mt-1 w-100"),
            dbc.Placeholder(color="warning", size="xl", className="me-1 mt-1 w-100"),
            dbc.Placeholder(color="danger", size="lg", className="me-1 mt-1 w-100"),
            dbc.Placeholder(color="info", size="xl", className="me-1 mt-1 w-100"),
            dbc.Placeholder(color="light", size="lg", className="me-1 mt-1 w-100"),
            dbc.Placeholder(color="dark", size="xl", className="me-1 mt-1 w-100"),
            ],
            id="real-time-rename"
        ), # Show new file name
        dbc.Row([], id="down-btn-items") # download button
    ])
)


def inputs_template(index):
    input_items = dbc.Row([
        dbc.Col(
            dmc.TextInput(
                label="Investigator",
                id={"type": "investigator", "index": index},
                w=200,
                debounce=200
            )
        ),
        dbc.Col(
            dmc.TextInput(
                label="Virus",
                id={"type": "virus-name", "index": index},
                w=200,
                debounce=200
            )
        ),
        dbc.Col(
            dmc.NumberInput(
                label="Plate number",
                id={"type": "plate-number", "index": index},
                w=200,
                value=1,
                debounce=200
            )
        ),
        dbc.Col(
            dmc.TextInput(
                label="Additional information",
                id={"type": "additional-info", "index": index},
                w=200,
            )
        ),
        dbc.Col(
            dcc.DatePickerSingle(
                placeholder="Date analysed",
                id={"type": "date-analysed", "index": index},
                date=date.today(),
                number_of_months_shown=3,
                with_portal=True,
                clearable=True,
            )
        ),
    ])
    return dmc.Paper([
        dmc.Text(index, id={"type": "old-name", "index": index}), # Old file name
        input_items, # Inputs
        dmc.Text(
            id={"type": "new-name", "index": index},
            size="lg",
            style={"textAlign":"center"}
        ),
        html.Span(style={"padding": "25px"})
        ],
        p='md', radius='lg', withBorder=True, shadow='sm',
    )


def multiply_downolad_objs(filenames):
    return [
        dcc.Download(id={"type": "download-files", "index": filename})
        for filename in filenames
    ]


@callback(
    Output("real-time-rename", "children"),
    Input("files-input", "filename"),
    prevent_initial_call=True,
)
def show_editing_components(filenames):
    if filenames is None:
        raise PreventUpdate()
    edit_components = [inputs_template(filename) for filename in filenames]
    return edit_components


@callback(
    Output("down-btn-items", "children"),
    Input("files-input", "filename"),
    prevent_initial_call=True,
)
def show_download_button(filenames):
    if filenames is None:
        raise PreventUpdate()
    dwn_btn = dbc.Col([
            dbc.Button(
                "Download files",
                id='down-btn',
                color='warning',
                class_name='d-grid col-12 mt-5',
                size='lg',
                outline=True
            ),
        ] + multiply_downolad_objs(filenames)
    )
    return dwn_btn

@callback(
    Output({'type':'new-name', 'index': MATCH}, 'children'),
    Input({'type':'investigator', 'index': MATCH}, 'value'),
    Input({'type':'virus-name', 'index': MATCH}, 'value'),
    Input({'type':'plate-number', 'index': MATCH}, 'value'),
    Input({'type':'date-analysed', 'index': MATCH}, 'date'),
    Input({"type": "old-name", "index": MATCH}, 'children'),
    Input({"type": "additional-info", "index": MATCH}, 'value'),
)
def real_time_update_filename(investigator, virus, plate, date_analysed, oldname, additional_info):
    if date_analysed is None:
        raise PreventUpdate()
    date_object = date.fromisoformat(date_analysed)
    additional_info = "" if additional_info is None else additional_info
    additional_info = re.sub(r"\s|,", "_", additional_info)

    return f"{investigator.capitalize()}_{virus}_P{plate}_{additional_info}_{date_object.strftime('%d%m%Y')}.{oldname.split('.')[-1]}"


@callback(
    Output({"type": "download-files", "index": MATCH}, "data"),
    Input("down-btn", "n_clicks"),
    State("files-input", "filename"),
    State("files-input", "contents"),
    State({'type':'new-name', 'index': MATCH}, 'children'),
    State({'type':'new-name', 'index': MATCH}, 'id'),
    prevent_initial_call=True
    # State({"type": "download-files", "index": MATCH}, 'id'),
)
def download_files(n_clicks, filenames, filecontents, newfile_name, dwn):
    if n_clicks is None:
        raise PreventUpdate()
    files = dict(zip(filenames, filecontents))

    content = files[dwn['index']].split(",")[1]
    data = {
        "content": content,
        "base64": True,
        "filename": newfile_name,
        "type": "application/vnd.ms-excel"
    }
    return data


if __name__ == "__main__":
    app.run(debug=True)