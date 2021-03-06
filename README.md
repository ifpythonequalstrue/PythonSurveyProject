# PythonSurveyProject

Projecto final para Jovenes a Programar, en el cual creamos una applicacion Flask que obtenga datos de GoogleSheets y los procese.

## Getting Started

Instrucciones para utilizar esta applicacion.

### Requerimientos

* [Python 3](https://www.python.org/downloads/release/python-363/)
* [Flask](https://github.com/pallets/flask)
* [GoogleSheets API v4](https://developers.google.com/sheets/api/quickstart/python) 
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
{"<Nombre de cabezal o numbero de cabeal>": ["<Filtro>", "<Valor para el filtro>"]}
```

Por defecto (basado en config.json) los filtros tienen los siguientes nombres:

Numericos:
* Equals 
* MoreThan 
* LessThan 
* MoreOrEquals 
* LessOrEquals

Para Strings:
* StartsWith 
* EndsWith 
* Exact
* In
* InMatchCase

Los filtros numericos solo se pueden utilizar para numeros enteros y floats.
Los filtros para strings tambien pueden ser usados para valores numericos, pero Exact funciona igual que Equals.


Ejemplo en Python:

```
import requests
import json 

parametros = {"Edad": ["MoreOrEquals", 10], 3: ["LessOrEquals", 5]}

r = requests.get("http://127.0.0.1:5000/microdatos", params=({"filters": json.dumps(parametros)})))
```

El resultado sera (Asumiendo que los parametros sean validos), un archivo csv el cual contiene los cabezales, y cualquier fila donde
se cumpla que "Edad" sea mayor o igual a 10, y el cabezal 3 contenga valores igual o menor que 5.


### Filtros para cabezales

Por el momento hay dos tipos de filtros para cabezales:

* Include
* Exclude

Include permite indicar que cabezales se quiere que se devuelvan, ignorando el resto, Exclude realiza la operacion opuesta.


Ejemplo en Python:

```
import requests
import json

parametros = {"include": ["Nombre", "Edad", 3, 4]}

r = requests.get("http://127.0.0.1:5000/microdatos", params=({"header_filters": json.dumps(parametros)}))
```

El resultado sera que el archivo csv solo contenga los primeros 4 cabezales (En el caso de el ejemplo, Nombre y Edad son 2 de ellos) y las demas filas las cuales contienen los valores correspondientes a los cabezales.
