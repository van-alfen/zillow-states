
import pathlib
import json
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State


main_file_path = pathlib.Path(__file__)
parent_folder = main_file_path.parent


# Zillow Data
data_file = parent_folder / 'assets' / 'data' / 'zillow-state-data.csv'
zillow_data_raw = pd.read_csv(data_file)

# geo json file
geo_json_file = parent_folder / 'assets' / 'data' / 'us-states.json'
geo_json_file = json.load(open(geo_json_file, 'r'))

# drop the columns: RegionID, SizeRank, RegionType, StateName
zillow_data_raw.drop(columns=['RegionID', 'SizeRank', 'RegionType', 'StateName'], inplace=True)

# reshape the data to panel structure instead of each date having its own column
zillow_data = zillow_data_raw.melt(id_vars=['RegionName'], var_name='Date', value_name='ZHVI')

# sort by region name and date
zillow_data.sort_values(by=['RegionName', 'Date'], inplace=True)

# convert string date to datetime
zillow_data['Date'] = pd.to_datetime(zillow_data['Date'])

# only keep the december observations
zillow_data = zillow_data[zillow_data['Date'].dt.month == 12]

# create year column
zillow_data['Year'] = zillow_data['Date'].dt.year

# rename region name column to state
zillow_data = zillow_data.rename(columns={'RegionName': 'State'})

# ensure state and year are unique
assert zillow_data[['State', 'Year']].duplicated().sum() == 0

# drop date
zillow_data.drop(columns=['Date'], inplace=True)

# order year after state
zillow_data = zillow_data[['State', 'Year', 'ZHVI']]

# year over year change
zillow_data['YOY'] = zillow_data.groupby('State')['ZHVI'].pct_change(fill_method=None)

# convert to percentage
zillow_data['YOY'] = zillow_data['YOY'] * 100

# drop missing values
zillow_data.dropna(subset=['YOY'], inplace=True)

# convert state names to state abbreviations
state_abbreviations = {
	'Alabama': 'AL',
	'Alaska': 'AK',
	'Arizona': 'AZ',
	'Arkansas': 'AR',
	'California': 'CA',
	'Colorado': 'CO',
	'Connecticut': 'CT',
	'Delaware': 'DE',
	'Florida': 'FL',
	'Georgia': 'GA',
	'Hawaii': 'HI',
	'Idaho': 'ID',
	'Illinois': 'IL',
	'Indiana': 'IN',
	'Iowa': 'IA',
	'Kansas': 'KS',
	'Kentucky': 'KY',
	'Louisiana': 'LA',
	'Maine': 'ME',
	'Maryland': 'MD',
	'Massachusetts': 'MA',
	'Michigan': 'MI',
	'Minnesota': 'MN',
	'Mississippi': 'MS',
	'Missouri': 'MO',
	'Montana': 'MT',
	'Nebraska': 'NE',
	'Nevada': 'NV',
	'New Hampshire': 'NH',
	'New Jersey': 'NJ',
	'New Mexico': 'NM',
	'New York': 'NY',
	'North Carolina': 'NC',
	'North Dakota': 'ND',
	'Ohio': 'OH',
	'Oklahoma': 'OK',
	'Oregon': 'OR',
	'Pennsylvania': 'PA',
	'Rhode Island': 'RI',
	'South Carolina': 'SC',
	'South Dakota': 'SD',
	'Tennessee': 'TN',
	'Texas': 'TX',
	'Utah': 'UT',
	'Vermont': 'VT',
	'Virginia': 'VA',
	'Washington': 'WA',
	'West Virginia': 'WV',
	'Wisconsin': 'WI',
	'Wyoming': 'WY',
}
zillow_data['State'] = zillow_data['State'].map(state_abbreviations)









# ----------------------------
# instantiate app
app = Dash( __name__, external_stylesheets=[dbc.themes.SANDSTONE] )

# change what is shown in the browser tab
app.title = 'Zillow Map'

# the app layout
app.layout = dbc.Container(
	children=[
		# title
		html.H1('Change in Zillow Home Value Index', className='text-center mt-5'),
		# chart
		dcc.Graph(
			id='zillow_chart',
			className='m-5',
			config={'displayModeBar': False},
		),
		# slider for year
		dcc.Slider(
			id='year_slider',
			min=zillow_data['Year'].min(),
			max=zillow_data['Year'].max(),
			step=1,
			value=zillow_data['Year'].max(),
			marks={str(year): str(year) for year in zillow_data['Year'].unique()},
		),
	],
	fluid=True,
)


# callback --- update the chart
@app.callback(
	Output('zillow_chart', 'figure'),
	Input('year_slider', 'value'),
)
def update_chart(slider_input):

	subset_df = zillow_data[zillow_data['Year'] == slider_input]

	state_map = px.choropleth(
		subset_df,
		locations='State',
		locationmode='USA-states',
		color='YOY',
		scope='usa',
		# title=f'Year over Year Change in ZHVI in {slider_input}',
		color_continuous_scale='RdYlGn',
		range_color=(-20, 30),
	)
	# make the map larger
	# state_map.update_layout(height=800)
	return state_map




# run the app
if __name__ == '__main__':
	app.run_server(debug=True)
