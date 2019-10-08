PyPrimitiva
===========

PyPrimitiva es un sencillo script escrito en Python 3.7 que comprueba los aciertos del usuario en la Lotería Primitiva española.

El script envía un correo electrónico con el resultado del sorteo y los aciertos de cada columna a las direcciones especificadas. Además incorpora la posibilidad de registrar en una base de datos MongoDB cada uno de los resultados, apuestas, fechas, y números acertados de cada uno de los sorteos.

Objetivo
----------
 - Simplificar la comprobación de varias apuestas / columnas para
   diferentes usuarios.
 - Notificar automáticamente los resultados cada uno de los días de
   sorteo.
 - Registrar cada uno de los sorteos en una base de datos que permita un
   posterior análisis de resultados o estadísticas.   

Ejemplo
-------
Gracias al módulo [Feedparser](https://pypi.python.org/pypi/feedparser) y al [RSS oficial con los resultados de la Primitiva](http://www.loteriasyapuestas.es/es/la-primitiva/resultados/.formatoRSS) que ofrece la ONLAE, obtener los resultados de cada sorteo es una tarea sencilla. 

```python
import feedparser

feed_url = "http://www.loteriasyapuestas.es/es/la-primitiva/resultados/.formatoRSS"

def parse_feed(feed_url):
    feed = feedparser.parse(feed_url)
    raw_date = feed.entries[1]["title"]
    raw_text = feed.entries[1]["description"]
    return raw_date, raw_text
```

A partir de aquí, invocamos cada una de las funciones presentes en el script para extraer los números coincidentes, el número complementario, el reintegro o la fecha entre otros. También el modo en el que gestionamos el output del programa, como su envío por email o el registro de sus resultados en la base de datos.

Instalación
-----------
PyPrimitiva requiere el módulo Feedparser, PyMongo y Python DotEnv.

    $ pip install -r requirements.txt

Una vez instaladas las dependencias, renombramos el fichero `.env.example` alojado en la raíz del programa y lo llamamos `.env` 

Este fichero será el encargado de guardar las variables de configuración del usuario, tales como la URI de la base de datos MongoDB o la cuenta de Gmail desde la que se enviarán las notificaciones. 

Para ello, editamos los valores de configuración establecidos inicialmente por los de nuestro usuario.

```
DB_URI=mongodb://localhost:27017
EMAIL_USERNAME=nombreUsuarioEmail
EMAIL_PASSWORD=passwordEmail
EMAIL_FROMADDRS=emisor@email.com
EMAIL_TOADDRS=["receptor@email.com"] 
PARTICIPANTE=Hurley
PARTICIPACIONES=[[4,8,15,16,23,42]]
```

En el caso de `DB_URI` se define por defecto un servidor MongoDB activo en local. Si queremos utilizar uno remoto necesitaremos su URI a la que apuntaremos con el driver.

Una opción es mediante una cuenta gratuita en [MLab](https://mlab.com/), con la que podremos obtener la `URI` necesaria.

    DB_URI = mongodb://<dbuser>:<dbpassword>@<dbdomain:port>/<dbname>


Tras esto, editamos las variables `EMAIL_USERNAME` con el nombre del usuario de la cuenta de Gmail desde la que enviaremos las notificaciones y su respectiva contraseña. Por ejemplo:

    EMAIL_USERNAME=john.doe
    EMAIL_PASSWORD=mySecretPassword

Seguidamente, en `EMAIL_FROMADDRS` editamos el valor correspondiente a la cuenta de correo desde la que se enviarán las notificaciones. 

```
EMAIL_FROMADDRS=john.doe@gmail.com
```

Posteriormente, en `EMAIL_TOADDRS` introducimos los destinatarios. Es posible configurar el programa para que más de una cuenta de correo reciba simultáneamente las notificaciones de los aciertos. 

Es importante introducir estos valores entre comillas dentro de los corchetes correspondientes a la lista, independientemente del número de destinatarios que queramos incluir.

    EMAIL_TOADDRS=["hurley@mail.com", "peter.griffin@mail.com" ]

Introducimos el nombre del participante en el campo `PARTICIPANTE`.

```
PARTICIPANTE=Hurley
```

Por último, definimos las diferentes combinaciones que queremos comprobar cada jueves y sábado. 

Es posible configurar múltiples participaciones. Tan solo tenemos que definirlas como una nueva lista de números dentro de la lista principal. 

```
PARTICIPACIONES=[[2,7,21,24,30,42],[10,19,20,25,39,42]]
```

Uso
---

La mejor opción es configurar una tarea programada para que PyPrimitiva se ejecute diariamente a las 00:00 h.  

El script comprobará primero si es jueves o sábado (días en los que hay sorteo) y posteriormente, si la anterior condición se cumple, invocará la función `is_updated()` dentro de `main()`.

Si el feed del sorteo se ha actualizado con los nuevos resultados, la función `main()` continuará ejecutándose y se obtendrá el nuevo output. Si por el contrario no se ha actualizado, el programa volverá a intentarlo tras esperar 300 segundos.

Tareas pendientes
-----
 - Refactorización. 
 - Manejo de excepciones y errores.

Contribución
------------
 - Comprobar incidencias abiertas o abrir una nueva ante cualquier bug
   identificado. 
 - Proponer nuevas ideas y funcionalidades.

PyPrimitiva es fácilmente adaptable al resto de sorteos de loterías para los que la ONLAE dispone de [canales RSS](http://www.loteriasyapuestas.es/es/canales-rss). 

Las principales modificaciones a realizar en el código para que devuelva resultados de otro sorteo se centran en las variables locales `start` y `stop` de las funciones que parsean los resultados (`combinación()`, `reintegro()` o `complementario()`) .

Licencia
--------
[GNU General Public License v3.0](https://github.com/Toolson12/pyPrimitiva/blob/master/LICENSE)


