# -*- coding: utf-8 -*-


import dash
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import geopandas as gpd
import plotly.express as px
import pandas as pd
import dash_table
# import pandas as pd
import dash_table_experiments as dt


df = pd.read_csv(r'prestadores_CB3_DATA_STUDIO_QGIS_IV.csv')
df['hover_data'] = '<b>' + df.Apellido + ' ' + df.Nombre +'</b></br>' + df.Direccion + \
                   '</br>' + df.name_depto + ', ' + df.name_prov

# -------------------------------------------------------
# APP DE DASH
# -------------------------------------------------------

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}]
                )
server = app.server
alert = dbc.Alert("Por favor complete todos ls campos para poder georreferenciar.",
                  color="danger",
                  duration = 3000,
                  # dismissable=True
                  )  # use dismissable or duration=5000 for alert to close in x milliseconds
app.title = 'Georreferenciación de Prestadores  '
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H1("Georreferenciación de prestadores",
                        # className='text-center text-primary, mb-4'
                 ),
                ], width = 12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id = 'mapa',
                      config={
                          # 'displayModeBar': False,
                          # 'displaylogo': False,
                          # 'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian', 'hoverClosestCartesian',
                          #                            'toggleSpikelines']
                      },
            ),
        ], width = 9),
        dbc.Col([
            dbc.Row([
                    dcc.Dropdown(
                               id='especialidad-dpdn',
                               options=[{'label': x.title(), 'value': x} for x in sorted(df.descripcion.unique())],
                               value=['Dermatología'],
                               placeholder="Seleccione especialidad",
                               # bs_size="sm",
                               multi=True,
                               # style=dict(
                               #     width='100%',
                               #     display='inline-block',
                               #     # verticalAlign="middle",
                               #     fontSize= 10,
                               #     height = "100%",
                               # ),
                           ),
                    ]
                ),
            dbc.Row(
                dcc.Dropdown(
                             id='prov-dpdn',
                             options=[{'label': x.title(), 'value': x} for x in sorted(df.name_prov.unique())],
                             value=['CORDOBA'],
                            placeholder="Seleccione provincia",
                            multi=True,
                    #         style=dict(
                    #             width='100%',
                    #             display='inline-block',
                    #             fontSize=10,
                    #             height = "100%",
                    # )
                )
            ),
            dbc.Row(
                dcc.Dropdown(
                             id='depto-dpdn',
                             options=[],
                             value=[],
                             placeholder="Seleccione departamento",
                             multi=True,
                    #          style=dict(
                    #             width='100%',
                    #             display='inline-block',
                    #             fontSize=10,
                    #             height = '100%',
                    # )
                ),
        ),
    ], width = 3),
    dbc.Row(
        dbc.Col(
            html.Div(
                id = "alert_prov",
                children = []
            )
        )
    ),
    dbc.Row(
        dbc.Col(
            html.Div(
                id="alert_map",
                children = []
            )
        )
    )
    ]),
    dbc.Row(
        dbc.Col([
            dash_table.DataTable(
                id='table-prestador',
                columns=[
                    {'name': 'Direccion', 'id': 'Direccion'},
                    {'name': 'Departamento', 'id': 'name_depto'},
                    {'name': 'Provincia', 'id': 'name_prov'}
                ],
                page_action="native",
                page_size=10,
                style_as_list_view=True,
                style_cell={
                    # 'font_family': 'cursive',
                    # 'font_size': '8px',
                    # 'padding': '1px',
                    # 'text_align': 'center'
                },
            ),
        ], width=12),
    ),
])

#---------------------------------------------------------------
# Callback
#---------------------------------------------------------------

# Llenamos los departamentos
@app.callback(
    Output('depto-dpdn', 'options'),
    Output('depto-dpdn', 'value'),
    Output("alert_prov", "children"),
    Input('prov-dpdn', 'value'),
)
def set_cities_options(provincia):
    if len(provincia) > 0:
        if type(provincia) == 'str':
            dff = df[df.name_prov == provincia]
        else:
            dff = df[df.name_prov.isin(provincia)]

        departamentos = [{'label': c.title(), 'value': c} for c in sorted(dff.name_depto.unique())]
        values_selected = [x['value'] for x in departamentos]
        return departamentos, values_selected, dash.no_update
    elif len(provincia) == 0:
        return dash.no_update, dash.no_update, alert

# Graficamos
@app.callback(
    Output('mapa', 'figure'),
    Output("alert_map", "children"),
    Output('table-prestador', 'data'),
    [Input('prov-dpdn', 'value'),
     Input('depto-dpdn', 'value'),
     Input('especialidad-dpdn','value')]
)
def update_graph(provincia, selected_dropdown_value, especialiadad):
    if len(especialiadad) >0:
        if len(provincia) > 0:
            if len(selected_dropdown_value) > 0:
                if type(selected_dropdown_value) == 'str':
                    dff = df[(df.name_depto.isin(selected_dropdown_value)) & (df.descripcion.isin(especialiadad)) & (df.name_prov.isin(provincia))]
                    if dff.empty:
                        print(dff)
                        # print('------------------------------------------------------------')
                    # print(selected_dropdown_value)
                    # print(especialiadad)
                else:
                    dff = df[(df.name_depto.isin(selected_dropdown_value)) & (df.descripcion.isin(especialiadad)) & (df.name_prov.isin(provincia))]
                    if dff.empty:
                        return dash.no_update, alert, dash.no_update
                    # print(selected_dropdown_value)
                    # print(especialiadad)
                
                # color_discrete = {'Dermatología': 'rgb(255,0,0)', 'Cardiología': 'rgb(0,255,0)', 'Pediatría': 'rgb(0,0,255)'}
                fig = px.scatter_mapbox(dff, lat="DirGeoY", lon="DirGeoX",
                                        color = "descripcion",
                                        # color_discrete_map=color_discrete,
                                        # hover_name="Apellido",
                                        # hover_data=['hover_data'],
                                        custom_data=['Apellido', 'Nombre', 'Direccion', 'name_prov', 'name_depto'],
                                        # c=dff.descripcion,
                                        # color_discrete_sequence=["fuchsia"],
                                        zoom = 5,
                                        )
                fig.update_layout(mapbox_style="open-street-map",
                                  margin={"r":0,"t":0,"l":0,"b":0},  # remove the white gutter between the frame and map
                                  # legend=dict(bgcolor='yellow'),
                                  hoverlabel=dict(
                                    bgcolor="white",  # white background
                                    font_size=8,  # label font size
                                    font_family="Inter"),

                )
                fig.update_traces(
                    opacity=0.5,
                    hovertemplate="<br>".join([
                        "Prestador: %{customdata[0]} %{customdata[1]}",
                        "Direccion: %{customdata[2]}",
                        "%{customdata[3]}, %{customdata[4]}"
                    ])
                )
                return fig, dash.no_update, dff.to_dict(orient='records')
            elif len(selected_dropdown_value) == 0:
                return dash.no_update, alert, dash.no_update
        elif len(provincia) == 0:
            return dash.no_update, alert, dash.no_update
    elif len(especialiadad) == 0:
        return dash.no_update, alert, dash.no_update

if __name__ == '__main__':
    app.run_server(debug=False,  host='0.0.0.0', port = 8050)

