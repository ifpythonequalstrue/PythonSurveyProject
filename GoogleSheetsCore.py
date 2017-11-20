import json
import gspread
import FilterCore
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
sheet_key = json.load(open('config.json'))['google_sheet']
sheet = client.open_by_key(sheet_key).sheet1

def return_all_values():
	return sheet.get_all_values()

def return_all_values_csv(params=None):
	all_values = return_all_values()
	if params != None:
		all_values = filter_headers(params, all_values)
	if all_values == None:
		return None
	value_str = ''
	for value in all_values:
		for column in value:
			if value[-1] != column:
				value_str += column + ', '
			else:
				value_str += column
		if all_values[-1] != value:
			value_str += '\n'
	return value_str

def filter_headers(params, all_values):
	if "header_filters" in params:
		all_values = FilterCore.validate_filters(all_values, params["filters"])
	if all_values != None:
		if "filters" in params:
			all_values = FilterCore.filter_headers(all_values, params["header_filters"])
			return all_values
	else:
		print("there are no filters")
		return None
		
