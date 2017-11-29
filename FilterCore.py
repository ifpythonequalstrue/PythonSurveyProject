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
					if not (int(filter) -1) in numeric_filters: 
						numeric_filters.append(int(filter) -1)
				else:
					return None
					
		numeric_filters.sort()
		return numeric_filters

	filter_type = ''
	if "Include" in header_filters and "Exclude" in header_filters:
		return None 
	elif "Include" in header_filters:
		filter_type = "Include"
	elif "Exclude" in header_filters:
		filter_type = "Exclude"
	else:
		return None	
	
	number_filters = translate_to_numeric()
	
	if number_filters != None:
		header_filters[filter_type] = number_filters
		for filter in header_filters[filter_type]:
			if filter > len(spread_values[0]):
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
				if "Include" in valid_filters:
					if x in valid_filters["Include"]:
						new_row.append(row[x])
				elif "Exclude" in valid_filters:
					if not x in valid_filters["Exclude"]:
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
		
def validate_filters(spread_values, filters):
	try:
		headers = spread_values[0]
		new_filters = {}
		
		for filter in filters.keys():
			if str(filter).isdigit():
				if int(filter) <= len(headers):
					value = filters[filter]
					new_filters[headers[int(filter) -1]] = value
				else:
					raise InvalidFilter
			else:
				new_filters[filter] = filters[filter]
				
		filters = new_filters
		non_headers = spread_values[1:]
		cleaned_up_filters = []
		
		for header_to_filter, filter_to_apply in filters.items():
			column = headers.index(header_to_filter)
			if header_to_filter in headers:
				if filter_to_apply[0] in regular_filters[0]["number_filters"]:
					for row_number in range(len(non_headers) + 1): 
						if row_number < len(non_headers):
							if non_headers[row_number] != '':
								if int_or_float(non_headers[row_number][column]):
									if int_or_float(filter_to_apply[1]):
										cleaned_up_filters.append({"column": column,
																	"filter": filter_to_apply[0],
																	"value": convert_int_or_float(filter_to_apply[1])})
										break
									else:
										raise InvalidFilter #Value of filter to apply is not a number
								else:
									raise InvalidFilter #First value != '' in the column is not a number
						else:
							raise InvalidFilter #None of the values in the column are valid
							
				elif filter_to_apply[0] in regular_filters[0]["string_filters"]:
					cleaned_up_filters.append({	"column": column, 
												"filter": filter_to_apply[0],
												"value": filter_to_apply[1]})
				else:
					raise InvalidFilter
			else:
				raise InvalidFilter
				
		return filter_manager(spread_values, cleaned_up_filters)
	except InvalidFilter:
		return None

def filter_manager(spread_values, filters):
	headers = spread_values[0]
	for x in range(len(filters)):
		spread_values = actual_filters(spread_values, filters[x], headers)
		spread_values.insert(0, headers)
	return spread_values
		
def actual_filters(spread_values, filters, headers):
	new_spread = []
	for x in range(len(spread_values)):
		if spread_values[x] != headers:
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
					
			elif filters["filter"] == regular_filters[0]["string_filters"][2]:				#Exact
				if filters["value"] == spread_values[x][filters["column"]]:
					new_spread.append(spread_values[x])
					
			elif filters["filter"] == regular_filters[0]["string_filters"][3]:				#In
				if filters["value"].lower() in spread_values[x][filters["column"]].lower():
					new_spread.append(spread_values[x])
					
			elif filters["filter"] == regular_filters[0]["string_filters"][4]:				#In Match Case
				if filters["value"] in spread_values[x][filters["column"]]:
					new_spread.append(spread_values[x])

	return new_spread

