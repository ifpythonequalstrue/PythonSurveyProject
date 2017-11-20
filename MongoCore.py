from pymongo import MongoClient
from datetime import datetime
import json

pymongo_uri = json.load(open('config.json'))['pymongo_uri']

client = MongoClient(pymongo_uri)
db = client.survey_thing
collection = db.flask_logs

def insert_document(request, response):
	service = str(request.url_rule)
	date = str(datetime.now())
	status_code = response.status_code
	status = response.status[4:]
	content_lenght = response.content_length
	content_type = response.content_type
	if request.authorization != None:
		user = request.authorization['username']
	else:
		user = None
	ip_dir = request.environ['REMOTE_ADDR']
	port = request.environ['REMOTE_PORT']
	collection.insert_one(
		{
			'servicio': service,
			'fecha_invocacion': date,
			'estado': {
				'codigo': status_code,
				'texto': status
			},
			'respuesta': {
				'largo': content_lenght,
				'tipo': content_type
			},
			'usuario': user,
			'direccion_consulta': [ip_dir, port]
		}
	)
	