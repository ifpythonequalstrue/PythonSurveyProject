import json
import MongoCore, GoogleSheetsCore, SentimentScript, AggregationScript
from functools import wraps
from flask import Flask, request, Response, make_response, render_template


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
			for k, v in params_from_json.items():
				if str(k).isdigit():
					if int(k) <= len(headers):
						if not v.split("_")[0] in valid_services:	#else: pass
							return []
					else:
						return []
				else:
					if k in headers:
						if not v.split("_")[0] in valid_services:	#else: pass
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
	#MongoCore.insert_document(request, response)
	return response

@app.route('/')
@requires_auth
def app_root():
	return render_template('test.html').format(username=request.authorization['username'])

@app.route('/microdatos')
@requires_auth
@requires_role
def app_microdatos():
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
	#response.headers["content-type"] = "text/plain; charset=utf-8"
	response.headers["content-Disposition"] = "attachment; filename=microdatos.csv"
	response.headers["content-type"] = "text/csv; charset=utf-8"
	return response

@app.route('/microdatos-console')
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
	response.headers["content-type"] = "text/plain; charset=utf-8"
	return response

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