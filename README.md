# PythonSurveyProject

Projecto final para Jovenes a Programar, en el cual creamos una applicacion Flask que obtenga datos de GoogleSheets y los procese.

## Getting Started

Instrucciones para utilizar esta applicacion.

### Requerimientos

* [Python 3](https://www.python.org/downloads/release/python-363/)
* [Flask](https://github.com/pallets/flask)
* [Gspread](https://github.com/burnash/gspread/) 
* [Watson](https://github.com/watson-developer-cloud/python-sdk)

### Instrucciones para utilizar esta applicacion

El archivo config.json contiene informacion necesaria para esta applicacion.
Los valores entre <> deben ser configurados para la applicacion funcione.

Simplente abriendo el archivo FlaskCore.py, Flask creara un servidor en localhost:5000/.

## Utilizando Filtros para el servicio de Microdatos

El servicio de Microdatos permite dos tipos de filtrado, filtros para el contenido de cada columna, y filtros para los cabezales.
Ambos tipos de filtros se pueden usar en conjunto (Sin embargo el filtrado de cabezales se realiza luego de los filtros, por lo cual es posible
excluir valores que fueron filtrados).
La applicacion requiere que estos filtros esten en formato json.

### Filtros comunes

El formato para utilizar uno de estos filtros es el siguiente (Ejemplo en forma de un diccionario python):

```
{"<Nombre de cabezal o numbero de cabeal>": "<Filtro>_<Valor para el filtro>"}
```

Por defecto (basado en config.json) los filtros tienen los siguientes nombres:

* Equals 
* MoreThan 
* LessThan 
* MoreOrEquals 
* LessOrEquals

* StartsWith 
* EndsWith 
* Find 
* FindMatchCase
* In
* InMatchCase


Ejemplo en Python:

```
import requests
import json 

parametros = {"Edad": "MoreOrEquals_10", 3: "LessOrEquals_5"}

r = requests.get("http://127.0.0.1:5000/microdatos", params=({"filters": json.dumps(parametros)})))
```

El resultado sera (Asumiendo que los parametros sean validos), un archivo csv el cual contiene los cabezales, y cualquier fila donde
se cumpra que "Edad" sea mayor o igual a 10, y el cabezal 3 contenga valores igual o menor que 5.


### Filtros para cabezales

Por el momento hay dos tipos de filtros para cabezales:

* Include
* Exclude

Include permite indicar que cabezales se quiere que se devuelvan, ignorando el resto, Exclude realiza la operacion opuesta


Ejemplo en Python:

```
import requests
import json

parametros = {"include": [1, 2, 3]}

r = requests.get("http://127.0.0.1:5000/microdatos", params=({"header_filters": json.dumps(parametros)}))
```
