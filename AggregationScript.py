import GoogleSheetsCore
import json

# {"aggregation": "<Column_name or column_number>"}
def validate_aggregation(params):
	all_values = GoogleSheetsCore.return_all_values()
	headers = all_values.pop(0)

	if str(params["aggregation"]).isdigit():
		if (int(params["aggregation"])-1 <= len(headers)) and int(params["aggregation"])-1 >= 0:
			column = int(params["aggregation"])-1
	
	elif params["aggregation"] in headers:
		column = headers.index(params["aggregation"])
	else:
		return None
		
	return [column, all_values, headers[column]]
		
def aggregate_data(params, words=["amount", "percentage"]):
	validate = validate_aggregation(params)
	
	if validate != None:
		column, all_values, header = validate
	else:
		return None
	
	column_list = []
	for row in all_values:
		column_list.append(row[column])
	
	column_dict = {}
	for value in column_list:
		if not value in column_dict: 
			column_dict[value] = 1
		else:
			column_dict[value] += 1
			
	element_amount = 0
	for value in column_dict.keys():
		element_amount += column_dict[value]
		
	percentage = {}
	for element in column_dict.keys():
		if not element in percentage:
			percentage[element] = 0
		value = column_dict[element]/element_amount
		percentage[element] = round((column_dict[element]/element_amount) * 100, 2)
		
	return {words[0]: column_dict, words[1]: percentage} 

def aggregate_run_from_config():
	to_return = {}
	with open("config.json", encoding="UTF-8") as file:
		params = json.load(file)["aggregate_data"]["aggregation"]
		
	if check_cache_data():
		return load_aggregation_data()["aggregation_data"]
	else:
		for key in params.keys():
			aggregate = aggregate_data({"aggregation": key}, params[key])
			to_return[key] = aggregate
			
	cache_aggregation_data(to_return)
	return to_return

	
def load_aggregation_data():
	try:
		with open("aggregation_data.json", encoding="UTF-8") as file:
			json_data = json.load(file)
		return json_data
		
	except FileNotFoundError:
		json_data = {}
		
		with open("aggregation_data.json", "w", encoding="UTF-8") as file:
			json_data["spreadsheet_length"] = 0
			json_data["aggregation_data"] = ""
			json.dump(json_data, file, ensure_ascii=False)
			
		return load_aggregation_data()
		
def cache_aggregation_data(aggregation_data):
	json_data = {}
	all_values = GoogleSheetsCore.return_all_values()
	headers = all_values.pop(0)
	
	with open("aggregation_data.json", "w", encoding="UTF-8") as file:
		json_data["spreadsheet_length"] = len(all_values)
		json_data["aggregation_data"] = aggregation_data
		json.dump(json_data, file, ensure_ascii=False)
		
def check_cache_data():
	all_values = GoogleSheetsCore.return_all_values()
	headers = all_values.pop(0)
	return len(all_values) == load_aggregation_data()["spreadsheet_length"]