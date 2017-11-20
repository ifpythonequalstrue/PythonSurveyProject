"""
params={"filters":{json.dumps("<header_name or header_number>": "<filter>_<value>")},
		"header_filters":{json.dumps(<"include" or "exclude">: [<header_name or header number>, <header_name or header_number>]})}
	
"""

import json

with open("config.json", encoding="UTF-8") as file:
	regular_filters = json.load(file)["regular_filters"]


class InvalidFilter(Exception):
	pass


def validate_header_filters(spread_values, header_filters):

	def translate_to_numeric():
		numeric_filters = []
		for filter in header_filters[filter_type]:
			if not str(filter).isdigit():
				if filter in spread_values[0]:
					if not spread_values[0].index(filter) in numeric_filters:
						numeric_filters.append(int(spread_values[0].index(filter)))
				else:
					return None
			else:
				if int(filter) > 0:
					if not int(filter) in numeric_filters: 
						numeric_filters.append(int(filter) -1)
				else:
					return None
					
		numeric_filters.sort()
		return numeric_filters

	filter_type = ''
	if "include" in header_filters and "exclude" in header_filters:
		return None 
	elif "include" in header_filters:
		filter_type = "include"
	elif "exclude" in header_filters:
		filter_type = "exclude"
	else:
		return None	
	
	number_filters = translate_to_numeric()
	if number_filters != None:
		header_filters[filter_type] = number_filters
		for filter in header_filters[filter_type]:
			if filter > len(header_filters[filter_type]):
				return None	
		return header_filters
	else:
		return None 
	
def filter_headers(spread_values, header_filters):
	valid_filters = validate_header_filters(spread_values, header_filters)
	if valid_filters != None:
		new_spread = []
		for row in spread_values:
			new_row = []
			for x in range(len(row)):
				if "include" in valid_filters:
					if x in valid_filters["include"]:
						new_row.append(row[x])
				elif "exclude" in valid_filters:
					if not x in valid_filters["exclude"]:
						new_row.append(row[x])
			new_spread.append(new_row)
		return new_spread 	
	else:
		return None	
		
def int_or_float(value):
	try:
		int(value)
		return True
	except:
		try:
			float(value)
			return True
		except:
			return False
			
def convert_int_or_float(value):
	try:
		return int(value)
	except:
		return float(value)

def translate_filters(diccionary):
	new_diccionary = {}
	for key, value in diccionary.items():
		split_value = str(value).split("_")
		keyword = split_value[0]
		if len(split_value[1:]) == 1:
			new_diccionary[key] = [keyword, split_value[1]]
		else:
			new_diccionary[key] = [keyword, "_".join(split_value[1:])]
	return new_diccionary
		
def validate_filters(spread_values, filters):
	new_diccionary = translate_filters(filters)
	filters = new_diccionary
	try:
		headers = spread_values[0]
		new_filters = {}
		
		for filter in filters.keys():
			if str(filter).isdigit():
				if int(filter) <= len(headers):
					value = filters[filter]
					new_filters[headers[int(filter) -1]] = value
				else:
					print(0)
					raise InvalidFilter
			else:
				new_filters[filter] = filters[filter]
				
		filters = new_filters
		first_values = spread_values[1]
		cleaned_up_filters = []
		
		for filter_header, filter in filters.items():
			if filter_header in headers:
				if filter[0] in regular_filters[0]["number_filters"]:
					if int_or_float(first_values[headers.index(filter_header)]):
						if int_or_float(filter[1]):
							cleaned_up_filters.append({	"column": headers.index(filter_header), 
														"filter": filter[0],
														"value": convert_int_or_float(filter[1])})
						else:
							print(1)
							raise InvalidFilter
					else:
						print(2)
						raise InvalidFilter
				elif filter[0] in regular_filters[0]["string_filters"]:
					cleaned_up_filters.append({	"column": headers.index(filter_header), 
												"filter": filter[0],
												"value": filter[1]})
				else:
					raise InvalidFilter
			else:
				print(3)
				raise InvalidFilter
				
		return filter_manager(spread_values, cleaned_up_filters)
	except InvalidFilter:
		print("Somehow invalid")
		return None

def filter_manager(spread_values, filters):
	headers = spread_values.pop(0)
	for x in range(len(filters)):
		spread_values = actual_filters(spread_values, filters[x])
	spread_values.insert(0, headers)
	return spread_values
		
def actual_filters(spread_values, filters):
	new_spread = []
	for x in range(len(spread_values)):
	
		if filters["filter"] == regular_filters[0]["number_filters"][0]:				#Equals
			if filters["value"] == convert_int_or_float(spread_values[x][filters["column"]]):
				new_spread.append(spread_values[x])
				
		elif filters["filter"] == regular_filters[0]["number_filters"][1]:				#Less Than
			if filters["value"] < convert_int_or_float(spread_values[x][filters["column"]]):
				new_spread.append(spread_values[x])
				
		elif filters["filter"] == regular_filters[0]["number_filters"][2]:				#More Than
			if filters["value"] > convert_int_or_float(spread_values[x][filters["column"]]):
				new_spread.append(spread_values[x])
				
		elif filters["filter"] == regular_filters[0]["number_filters"][3]:				#Less or Equals
			if filters["value"] <= convert_int_or_float(spread_values[x][filters["column"]]):
				new_spread.append(spread_values[x])
				
		elif filters["filter"] == regular_filters[0]["number_filters"][4]:				#More or Equals
			if filters["value"] >= convert_int_or_float(spread_values[x][filters["column"]]):
				new_spread.append(spread_values[x])
				
		elif filters["filter"] == regular_filters[0]["string_filters"][0]:				#Starts With
			if spread_values[x][filters["column"]].lower().startswith(filters["value"].lower()):
				new_spread.append(spread_values[x])
				
		elif filters["filter"] == regular_filters[0]["string_filters"][1]:				#Ends With
			if spread_values[x][filters["column"]].lower().endswith(filters["value"].lower()):
				new_spread.append(spread_values[x])
				
		elif filters["filter"] == regular_filters[0]["string_filters"][2]:				#Find
			if filters["value"].lower() == spread_values[x][filters["column"]].lower():
				new_spread.append(spread_values[x])
				
		elif filters["filter"] == regular_filters[0]["string_filters"][3]:				#Find Match Case
			if filters["value"] == spread_values[x][filters["column"]]:
				new_spread.append(spread_values[x])
				
		elif filters["filter"] == regular_filters[0]["string_filters"][4]:				#In
			if filters["value"].lower() in spread_values[x][filters["column"]].lower():
				new_spread.append(spread_values[x])
				
		elif filters["filter"] == regular_filters[0]["string_filters"][5]:				#In Match Case
			if filters["value"] in spread_values[x][filters["column"]]:
				new_spread.append(spread_values[x])
	return new_spread

