import httplib2, os, json
import FilterCore
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-quickstart.json')
	
	store = Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else:
			credentials = tools.run(flow, store)
	return credentials

def return_all_values():
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
	service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
							
	with open("config.json", encoding="UTF-8") as file:
		json_config = json.load(file)
		spreadsheetId = json_config["spreadsheet_id"]
		spreadsheet_name = json_config["spreadsheet_name"]  
		spreadsheet_range = json_config["spreadsheet_range"]
		rangeName = spreadsheet_name + spreadsheet_range
	result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
	values = result.get('values', [[]])
	
	all_values = list(values)
	headers = all_values[0]
	answers = all_values[1:]

	clean_list = [headers]
	for value in answers:
		if len(value) < len(headers):
			missing_values = len(headers) - len(value)
			for missing_element in range(1, missing_values + 1):
				value.append('')
		clean_list.append(value)
	return clean_list
	
def return_all_values_csv(params=None, all_values=return_all_values()):
	if params != None:
		all_values = filter_headers(params, all_values)
	if all_values == None:
		return None #Filter was invalid

	csv_string = ''
	for spreadsheet_row in all_values:
		for element_from_row in spreadsheet_row:
			if spreadsheet_row[-1] != element_from_row:
				csv_string += element_from_row + ','
			else:
				csv_string += element_from_row
		if spreadsheet_row != all_values[-1]:
			csv_string += "\n"
			
	return csv_string

def filter_headers(params, all_values):
	if "filters" in params:
		all_values = FilterCore.validate_filters(all_values, params["filters"])
	if all_values != None:
		if "header_filters" in params:
			all_values = FilterCore.filter_headers(all_values, params["header_filters"])
			return all_values
		else:
			return all_values
	else:
		return None #Filter was invalid
		
def return_all_values_as_list(params=None, all_values=None):
	if all_values == None:
		all_values = return_all_values()
	
	if params != None:
		all_values = filter_headers(params, all_values)
	if all_values == None:
		return None	#Filter was invalid
		
	return all_values