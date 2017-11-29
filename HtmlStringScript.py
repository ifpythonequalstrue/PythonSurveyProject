import re, json
import GoogleSheetsCore

def html_table_as_string(all_values):
	if all_values != None:
	
		headers = all_values[0]
		html_string = '<tr>'
		
		for header in headers:
			header = re.sub(r'"', "&quot;", header)
			html_string += ('<th> <form action="/microdatos/parametros" method="post">' +
							'<input class="button" type="submit" name="header" value="{}"/></th>'.format(header))
		html_string += '</tr>'
			
		for row in all_values:
			if row != headers:
				html_string += '<tr>'
				for element in range(len(headers)):
					if element < len(row):
						string = re.sub(r'"', "&quot;", row[element])
						html_string += '<td>' + string + '</td>'
					else:
						html_string += '<td>' + '' + '</td>'
	
		return html_string
		
	else:
		return None #Shouldn't be necessary to have this but that's okay

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
	
def return_filter_html(header, all_values):
	with open("config.json", encoding="UTF-8") as file:
		json_stuff = json.load(file)
		filters = json_stuff['regular_filters'][0]
		microdata_services = json_stuff['microdata_services']

	headers = all_values[0]
	
	#Check if first value of column is a number
	column = headers.index(header)		
	for row in range(1, len(all_values) + 1): 
		if row != len(all_values):
			if column < len(all_values[row]):
				if not int_or_float(all_values[row][column]):
					filters = filters["string_filters"]
					break
				else:
					filters = filters["number_filters"] + filters["string_filters"]
					break
		else:
			return None
	
	#<option value="filter">filter</option>
	html_string = ''
	for filter in filters:
		if filter in microdata_services:
			html_string += "<option value={}>".format(filter)
			html_string += filter
			html_string += "</option>"
	
	return html_string
	
def return_header_filter_html(current_headers):
	with open("config.json", encoding="UTF-8") as file:
		filters = json.load(file)['microdata_services'][-2:]
	
	html_string = '<select name="header_filter" required>'
	
	for filter in filters:
		html_string += "<option value={}>".format(filter)
		html_string += filter
		html_string += "</option>"
		
	html_string += '</select><br/><br/>Seleccione cabezales a incluir o excluir:<br/><div class="inner_wrapper">'
	
	for header in current_headers:	
		html_string += '<input type="checkbox" name="values" value="{}"/> {}<br/>'.format(current_headers.index(header) +1,
																						  header)
	
	html_string += "</div><br/><br/>"
	return html_string
