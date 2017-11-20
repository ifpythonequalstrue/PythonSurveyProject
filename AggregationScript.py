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
		percentage[element] = round(column_dict[element]/element_amount, 3)
		
	return {words[0]: column_dict, words[1]: percentage} 

def aggregate_run_from_config():
	to_return = {}
	with open("config.json", encoding="UTF-8") as file:
		params = json.load(file)["aggregate_data"]["aggregation"]
		
	for key in params.keys():
		aggregate = aggregate_data({"aggregation": key}, params[key])
		to_return[key] = aggregate
		
	return to_return