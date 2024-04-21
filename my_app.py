from dash import Dash, html, dcc, callback, Output, Input
import dash_draggable
import plotly.express as px
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

# External CSS stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'https://codepen.io/chriddyp/pen/brPBPO.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

# Адаптивность диаграмм - встраивание в окно
style_dashboard = {
    "height": '100%',
    "width": '100%',
    "display": "flex",
    "flex-direction": "column",
    "flex-grow": "0"
}

style_controls = {
    "display": "grid",
    "grid-template-columns": "auto 1fr",
    "align-items": "center",
    "gap": "1rem"
}


# График 1: пузырьковая диаграмма с выбором по мерам
def build_bubble_fig(x="gdpPercap", y="lifeExp", size="pop", year_from=None, year_to=None):
    filtered_data = df

    if year_from and year_to:
        filtered_data = df[df.year.between(year_from, year_to)]

    latest_data = filtered_data.sort_values(["continent", "year"], ascending=False).drop_duplicates("country")

    return px.scatter(latest_data, x=x, y=y, size=size, color="continent", hover_name="country", size_max=60,
                      hover_data=["year"])


bubble_dash = html.Div([
    html.Table([
        html.Tr([
            html.Td([
                html.Span("По оси X")
            ], style={"white-space": "nowrap"}),
            html.Td([
                dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], value="gdpPercap", id='bubble-x', clearable=False)
            ], style={"width": "100%"})
        ]),
        html.Tr([
            html.Td([
                html.Span("По оси Y")
            ]),
            html.Td([
                dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], value="lifeExp", id='bubble-y', clearable=False),
            ])
        ]),
        html.Tr([
            html.Td([
                html.Span("Размер")
            ]),
            html.Td([
                dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], value="pop", id='bubble-size', clearable=False),
            ])
        ]),
    ], style={"margin": "0rem 1rem"}),
    dcc.Graph(id='bubble', figure=build_bubble_fig(), style=style_dashboard, responsive=True)
], style=style_dashboard, id="bubble-dash")


# График 2: зависимость разных показателей от года
def build_meas_vs_year_fig(active_countries, measure="pop"):
    linechart_countries = df[df.country.isin(active_countries)]
    return px.line(linechart_countries, x="year", y=measure, color="country", title="Показатели по годам")


meas_vs_year_dash = html.Div([
    html.Table([
        html.Tr([
            html.Td([
                html.Span("Активные страны")
            ], style={"white-space": "nowrap"}),
            html.Td([
                dcc.Dropdown(df.country.unique(), value=["United States", "China", "India"], multi=True,
                             id='dropdown-active-countries'),
            ], style={"width": "100%"}),
        ]),
        html.Tr([
            html.Td([
                html.Span("Мера")
            ]),
            html.Td([
                dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], value="pop", id='dropdown-measure', clearable=False)
            ]),
        ])
    ], style={"margin": "0rem 1rem"}),
    dcc.Graph(id='meas-vs-year', figure=build_meas_vs_year_fig(["United States", "China", "India"]),
              style=style_dashboard, responsive=True)
], style=style_dashboard, id="meas-vs-year-dash")


# График 3: топ-15 стран по популяции
def build_top_pop_fig(year_from=None, year_to=None):
    filtered_data = df

    if year_from and year_to:
        filtered_data = df[df.year.between(year_from, year_to)]

    latest_data = filtered_data.sort_values("year", ascending=False).drop_duplicates("country")
    top = latest_data.sort_values("pop", ascending=False)[:15][::-1]

    return px.bar(top, x="pop", y="country", title="Топ 15 стран по населению", hover_data=["year"])


top_pop_dash = html.Div([
    dcc.Graph(id='top-pop', figure=build_top_pop_fig(), style=style_dashboard, responsive=True)
], style=style_dashboard, id="top-pop-dash")


# График 4: круговая диаграмма по популяциям на континентах
def build_pop_pie_fig(year_from=None, year_to=None):
    filtered_data = df

    if year_from and year_to:
        filtered_data = df[df.year.between(year_from, year_to)]

    latest_data = filtered_data.sort_values("year", ascending=False).drop_duplicates("country")
    continent_data = latest_data.groupby("continent").sum()

    return px.pie(df, values="pop", names="continent", title="Население континентов", hole=.3)


pop_pie_dash = html.Div([
    dcc.Graph(id='pop-pie', figure=build_pop_pie_fig(), style=style_dashboard, responsive=True)
], style=style_dashboard, id="pop-pie-dash")


app.layout = html.Div([
    html.H1(children='Сравнение стран', style={'textAlign': 'center'}),
    dash_draggable.ResponsiveGridLayout([
        meas_vs_year_dash,
        bubble_dash,
        top_pop_dash,
        pop_pie_dash
    ], clearSavedLayout=True, layouts={
        "lg": [
            {
                "i": "bubble-dash",
                "x":7, "y": 10, "w": 7, "h": 13
            },
            {
                "i": "meas-vs-year-dash",
                "x": 0, "y": 0, "w": 7, "h": 13
            },
            {
                "i": "top-pop-dash",
                "x": 7, "y": 0, "w": 5, "h": 13
            },
            {
                "i": "pop-pie-dash",
                "x": 0, "y": 10, "w": 5, "h": 13
            }
        ]
    })
])


@callback(
    Output('meas-vs-year', 'figure'),
    Input('dropdown-active-countries', 'value'),
    Input('dropdown-measure', 'value')
)
def update_meas_vs_year_dash(active_countries, measure):
    return build_meas_vs_year_fig(active_countries, measure)


def extract_from_to(arg):
    year_from = None
    year_to = None
    if arg:
        if 'xaxis.range[0]' in arg:
            year_from = arg['xaxis.range[0]']
        if 'xaxis.range[1]' in arg:
            year_to = arg['xaxis.range[1]']

    return year_from, year_to


@callback(
    Output('bubble', 'figure'),
    Input('bubble-x', 'value'),
    Input('bubble-y', 'value'),
    Input('bubble-size', 'value'),
    Input('meas-vs-year', 'relayoutData'),
)
def update_bubble_dash(x, y, size, meas_vs_year_zoom):
    return build_bubble_fig(x, y, size, *extract_from_to(meas_vs_year_zoom))


@callback(
    Output('top-pop', 'figure'),
    Input('meas-vs-year', 'relayoutData'),
)
def update_top_pop_dash(meas_vs_year_zoom):
    return build_top_pop_fig(*extract_from_to(meas_vs_year_zoom))


@callback(
    Output('pop-pie', 'figure'),
    Input('meas-vs-year', 'relayoutData'),
)
def update_pop_pie_dash(meas_vs_year_zoom):
    return build_pop_pie_fig(*extract_from_to(meas_vs_year_zoom))


# # Run: gunicorn main:app
if __name__ == '__main__':
    app.run_server(debug=True)
