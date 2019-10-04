PyPrimitiva
===========

PyPrimitiva es un sencillo script escrito en Python 2.6 que comprueba los aciertos del usuario en la Lotería Primitiva española.

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

    import feedparser
    
    feed_url = "http://www.loteriasyapuestas.es/es/la-primitiva/resultados/.formatoRSS"
    
    def parse_feed(feed_url):
        feed = feedparser.parse(feed_url)
        raw_date = feed.entries[1]["title"]
        raw_text = feed.entries[1]["description"]
        return raw_date, raw_text

A partir de aquí, invocamos cada una de las funciones presentes en el script para extraer los números coincidentes, el número complementario, el reintegro o la fecha entre otros. También el modo en el que gestionamos el output del programa como su envío por email o el registro de sus resultados en la base de datos.

Instalación
-----------
PyPrimitiva requiere el módulo Feedparser y PyMongo.

    $ pip install feedparser
    $ pip install pymongo

En el caso de PyMongo, necesitaremos una base de datos MongoDB a la que apuntar con el driver. Una opción es mediante una cuenta gratuita en [MLab](https://mlab.com/), con la que podremos obtener la `URI` necesaria.

    URI = mongodb://<dbuser>:<dbpassword>@<dbdomain:port>/<dbname>


Tras esto, editamos la variable `my numbers` con el nombre del usuario que queramos y los números correspondientes a sus apuestas. 

    my_numbers = {"Hurley": [[4,8,15,16,23,42]]}

Seguidamente, editamos los datos correspondientes a nuestra cuenta de correo (parámetros de Gmail por defecto en el código).

    # Specifying the from and to addresses
    FROMADDRS = Cuenta de correo desde la que se envía el correo.
    TOADDRS = [Cuenta/s de correo que recibe/n los resultados]

    # Gmail Login
    USERNAME = 'Nombre de usuario de la cuenta de correo'
    PASSWORD = 'Contraseña de la cuenta de correo'

Uso
---
La mejor opción es dejar una tarea programada para que PyPrimitiva se ejecute diariamente a las 00:00 h.  

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


