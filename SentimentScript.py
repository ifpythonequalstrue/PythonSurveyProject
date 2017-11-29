import json
import GoogleSheetsCore
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SentimentOptions

def validate_sentiment(params):
	all_values = GoogleSheetsCore.return_all_values()
	headers = all_values.pop(0)
	
	if str(params["sentiment"]).isdigit():
		if (int(params["sentiment"])-1 <= len(headers)) and int(params["sentiment"])-1 >= 0:
			column = int(params["sentiment"])-1
		else:
			return None
	elif params["sentiment"] in headers:
		column = int(headers.index(params["sentiment"]))
	else:
		return None

	column_list = []
	for row in all_values:
		try:
			column_list.append(row[column])
		except:
			pass
	return [column_list, headers[column]]

def sentiment(params):
	column_data = validate_sentiment(params)
	
	if column_data != None:
		column_list, header = column_data 
		sentiment_data = json.load(open("config.json"))["sentiment_data"]
		
		natural_language_understanding = NaturalLanguageUnderstandingV1(version=sentiment_data["version"],
																		username=sentiment_data["username"],
																		password=sentiment_data["password"])
		
		sentiment_data = {"positivo": 0, "negativo": 0, "neutral": 0}
		
		for string in column_list:
			if len(string) >= 25:
				try:
					response = natural_language_understanding.analyze(text=string, features=Features(sentiment=SentimentOptions()))

					if response["sentiment"]["document"]["label"] == "positive":
						sentiment_data["positivo"] += 1
					elif response["sentiment"]["document"]["label"] == "negative":
						sentiment_data["negativo"] += 1
					elif response["sentiment"]["document"]["label"] == "neutral":
						sentiment_data["neutral"] += 1
				except:
					pass
					
		cache_sentiment_data({header: sentiment_data})
		return {header: sentiment_data}
		
	else:
		return None

def aggregate_run_from_config():
	with open("config.json", encoding="UTF-8") as file:
		params = json.load(file)["aggregate_data"]["sentiment"][0]
		
	if check_cache_data():
		return load_sentiment_data()["sentiment_data"]
		
	else:
		return sentiment({"sentiment": params})

def load_sentiment_data():
	try:
		with open("sentiment_data.json", encoding="UTF-8") as file:
			json_data = json.load(file)
		return json_data
		
	except FileNotFoundError:
		json_data = {}
		
		with open("sentiment_data.json", "w", encoding="UTF-8") as file:
			json_data["spreadsheet_length"] = 0
			json_data["sentiment_data"] = ""
			json.dump(json_data, file, ensure_ascii=False)
			
		return load_sentiment_data()

def cache_sentiment_data(sentiment_data):
	json_data = {}	
	all_values = GoogleSheetsCore.return_all_values()
	headers = all_values.pop(0)
	
	with open("sentiment_data.json", "w", encoding="UTF-8") as file:
		json_data["spreadsheet_length"] = len(all_values)
		json_data["sentiment_data"] = sentiment_data
		json.dump(json_data, file, ensure_ascii=False)
		
def check_cache_data():
	all_values = GoogleSheetsCore.return_all_values()
	headers = all_values.pop(0)
	return len(all_values) == load_sentiment_data()["spreadsheet_length"]
