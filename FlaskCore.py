import json
import MongoCore, GoogleSheetsCore, SentimentScript, AggregationScript, HtmlStringScript
from functools import wraps
from flask import Flask, request, Response, make_response, render_template, redirect

def check_auth(username, password):
	with open("config.json", encoding="UTF-8") as file:
		users = json.load(file)['users']
	
	for user in users:
		if user['username'] == username and user['password'] == password: 
			return True
	return False

def authenticate():
	return Response(
	'Could not verify your access level for that URL.\n'
	'You have to login with proper credentials', 401,
	{'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return f(*args, **kwargs)
	return decorated

def requires_role(f):
	@wraps(f)
	def role_check(*args, **kwargs):
		username = request.authorization['username']
		resource = request.url_rule
		
		with open("config.json", encoding="UTF-8") as file:
			json_load = json.load(file)
			config_users = json_load['users']
			config_roles = json_load['roles']
		
		role = ''
		for x in range(len(config_users)):
			if username == config_users[x]["username"]:
				role = config_users[x]["role"]
				break	
		if str(resource) in config_roles[role]["services"]:
			return f(*args, **kwargs)
		else:
			return Response(("Unathorized Service for your username"), 401)
	return role_check

def header_params_check(args, valid_services):
	if args != '':	#No params
		headers = GoogleSheetsCore.return_all_values()[0]
		params = {}
		
		if "filters" in args:
			params_from_json = json.loads(args["filters"])
			
			for header, filter_and_value in params_from_json.items():
			
				if str(header).isdigit():
					if int(header) <= len(headers):
						if not filter_and_value[0] in valid_services:	#else: pass
							return []
					else:
						return []
						
				else:
					if header in headers:
						if not filter_and_value[0] in valid_services:	#else: pass
							return []
					else:
						return []
						
			params["filters"] = params_from_json
			
		if "header_filters" in args:
			params_from_json = json.loads(args["header_filters"])
			
			if len(params_from_json) == 1:
				filter_type = ''
				if "Include" in params_from_json:
					filter_type = "Include"
				elif "Exclude" in params_from_json:
					filter_type = "Exclude"
				else:
					return []
					
				for value in params_from_json[filter_type]:
					if str(value).isdigit():
						if not int(value) <= len(headers):
							return []
					else:
						if not value in headers:
							return []
							
			params["header_filters"] = params_from_json
			
		return params
		if "filters" not in args and "header_filters" not in args:
			return []
		
app = Flask(__name__)

@app.after_request
def app_after_request(response):
	MongoCore.insert_document(request, response)
	return response

@app.route('/')
@requires_auth
def app_root():
	return render_template('root.html').format(username=request.authorization['username'])

microdata_table_parameters = {"current_table_list": None,
							  "default_table_list": GoogleSheetsCore.return_all_values(),
							  "current_filter": None,
							  "current_header": None}
							  
with open("config.json", encoding="UTF-8") as file:
	json_load = json.load(file)
	sheetname = json_load["spreadsheet_main_name"]
	sub_sheetname = json_load["spreadsheet_name"]
	
@app.route('/microdatos', methods=["GET", "POST"])
@requires_auth
@requires_role
def app_microdatos():
	if request.method == "GET":
		if microdata_table_parameters["current_table_list"] == None:	#Happens first or when current table is reset
			default_table_list = microdata_table_parameters["default_table_list"]
			microdata_table_parameters["current_table_list"] = default_table_list
			
			html_string = HtmlStringScript.html_table_as_string(default_table_list)
			return render_template("data_table_base.html", table=html_string, 
														   sheetname=sheetname,
														   sub_sheetname=sub_sheetname)

		if microdata_table_parameters["current_table_list"] != None and microdata_table_parameters["current_filter"] == None: #User probably reloaded page
			current_table_list = microdata_table_parameters["current_table_list"]
			html_string = HtmlStringScript.html_table_as_string(current_table_list)
			
			throwaway = "throwaway"
			if microdata_table_parameters["current_table_list"] == microdata_table_parameters["default_table_list"]:
				throwaway = ''	#To avoid showing download current table and reset table if you reload when default table is current table
			
			return render_template("data_table_base.html", table=html_string,
														   sheetname=sheetname,
														   sub_sheetname=sub_sheetname,
														   current_sheet_not_default=throwaway)

		if microdata_table_parameters["current_filter"] != None:	#There's a filter to be applied
			current_filter = microdata_table_parameters["current_filter"]
			with open("config.json", encoding="UTF-8") as file:
				microdata_services = json.load(file)["microdata_services"]
			
			parameters = header_params_check(current_filter, microdata_services)
			if len(parameters) == 0: #User probably sent an invalid POST somehow, or I messed up
				return(Response("I don't know how you did that, but it's not allowed anyways", 400))

			filter_failure = ''
			current_table_list = GoogleSheetsCore.return_all_values_as_list(parameters, microdata_table_parameters["current_table_list"])
			microdata_table_parameters["current_filter"] = None
			current_sheet_not_default='throwaway'	#Value doesn't really matter, just has to not be empty to show the other 2 buttons
			
			if current_table_list == None:
				filter_failure = "El valor que usted selecciono no es valido para ese filtro o para esa columna"
				current_table_list = microdata_table_parameters["current_table_list"]
				if current_table_list == microdata_table_parameters["default_table_list"]:
					current_sheet_not_default = ''	#Avoids showing download current table or reset table, if current table is the same as default table
			else:
				microdata_table_parameters["current_table_list"] = current_table_list
			
			html_string = HtmlStringScript.html_table_as_string(current_table_list)
			return render_template("data_table_base.html", table=html_string,
														   sheetname=sheetname,
														   sub_sheetname=sub_sheetname,
														   current_sheet_not_default=current_sheet_not_default,
														   filter_failure=filter_failure)
														   
	elif request.method == "POST":
		if "download_original" in request.form:
			return redirect("/microdatos_consola")
			
		elif "download_actual" in request.form:
			current_table_list = microdata_table_parameters["current_table_list"]
			microdata = GoogleSheetsCore.return_all_values_csv(all_values=current_table_list)
			response = make_response(microdata)
			response.headers["content-Disposition"] = "attachment; filename=microdatos.csv"
			response.headers["content-type"] = "text/csv; charset=utf-8"
			return response
			
		elif "reset_original" in request.form:
			microdata_table_parameters["current_table_list"] = None
			return redirect("/microdatos")
			
		else:
			return Response("Invalid content in POST method", 400)

@app.route('/microdatos_consola')
@requires_auth
@requires_role
def app_microdatos_console():
	parameters = None
	
	if len(request.args) > 0:
		with open("config.json", encoding="UTF-8") as file:
			microdata_services = json.load(file)['microdata_services']

		parameters = header_params_check(request.args, microdata_services)
		if len(parameters) == 0:	# invalid parameters
			return(Response("Invalid parameters", 400))
			
	microdata = GoogleSheetsCore.return_all_values_csv(parameters)
	if microdata == None:
		return(Response("One or more of the filters are invalid", 400))
		
	response = make_response(microdata)
	response.headers["content-Disposition"] = "attachment; filename=microdatos.csv"
	response.headers["content-type"] = "text/csv; charset=utf-8"
	return response

@app.route("/microdatos/parametros", methods=["POST", "GET"])
@requires_auth
@requires_role
def app_microdatos_parametros():
	if "header" in request.form:
		header = request.form["header"]
		microdata_table_parameters["current_header"] = header
		return render_template("filter_type_selection.html", header=header)
	
	if "filter" in request.form:
		header = microdata_table_parameters["current_header"]
		current_table_list = microdata_table_parameters["current_table_list"]
		return render_template("filter_type_selection.html", filter=HtmlStringScript.return_filter_html(header, current_table_list),
															 header=header)
		
	elif "header_filter" in request.form:
		list_current_headers = microdata_table_parameters["current_table_list"][0]
		html_string = HtmlStringScript.return_header_filter_html(list_current_headers)
	
		header = microdata_table_parameters["current_header"]
		return render_template("filter_type_selection.html", header_filter=html_string,
															 header=header)
	
	return redirect("/microdatos") #This shouldn't happen unless the user goes to this page first for some reason

@app.route("/microdatos/parametros/procesar", methods=["POST", "GET"])
@requires_auth
@requires_role
def app_microdatos_parametros_procesar():
	current_table_list = microdata_table_parameters["current_table_list"]
	
	if "filter" in request.form:
		filter_type = request.form["filter"]
		value = request.form["value"]
		header = microdata_table_parameters["current_header"]
		filter = {header: [filter_type, value]}
		
		microdata_table_parameters["current_filter"] = {"filters": json.dumps(filter)}
		return redirect("/microdatos")
	
	if "header_filter" in request.form:
		filter_type = request.form["header_filter"]
		list_headers = request.form.getlist("values")
		filter = {filter_type: list_headers}
		
		microdata_table_parameters["current_filter"] = {"header_filters": json.dumps(filter)}
		return redirect("/microdatos")
		
	return Response("Invalid content in POST method", 400)

@app.route("/datos_agregados")
@requires_auth
@requires_role
def app_aggregate_data():
	aggregation = AggregationScript.aggregate_run_from_config()
	sentiment = SentimentScript.aggregate_run_from_config()
	result = {"aggregation": aggregation, "sentiment": sentiment}
	response = make_response(json.dumps(result, ensure_ascii=False).encode("utf8"))
	response.headers["content-type"] = "application/json"
	return response
	
if __name__ == '__main__': 	
	app.run()