# -*- coding: utf-8 -*-

import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import feedparser
import pymongo
import smtplib
import time

feed_url = "http://www.loteriasyapuestas.es/es/la-primitiva/resultados/.formatoRSS"

## MongoDB handlers
URI = "mongodb://<dbuser>:<dbpassword>@<dbdomain:port>/<dbname>" # Editar con la URI de la base de datos
client = pymongo.MongoClient(URI)
db = client["lottery_db"]
coleccion_resultados = db["resultados"]
ultimo_sorteo = db["ultimo_sorteo"]

## Email handlers
USERNAME = 'Nombre de usuario de la cuenta de correo' # Editar con el nombre de usuario de la cuenta de correo
PASSWORD = 'Contraseña de la cuenta de correo' # Editar con la contraseña de la cuenta de correo
FROMADDRS = "Cuenta de correo desde la que se envía" # Editar con la dirección de correo que realiza el envío
TOADDRS = ["Cuenta/s de correo que recibe/n los resultados"] # Editar con las direcciones de envío separadas por comas

## Apuestas y apostantes
my_numbers = {"Hurley": [[4, 8, 15, 16, 23, 42]]} # Editar con el nombre y los números de cada apostante.


def parse_feed(feed_url):
    feed = feedparser.parse(feed_url)
    raw_date = feed.entries[1]["title"]
    raw_text = feed.entries[1]["description"]
    return raw_date, raw_text


def combinacion():
    raw_text = parse_feed(feed_url)[1]
    start = raw_text.find("<b>") + 3
    stop = raw_text.find("</b>")
    raw_numbers = raw_text[start:stop]
    numbers = []
    string_numbers = raw_numbers.split(" - ")
    for number in string_numbers:
        numbers.append(int(number))
    return numbers


def reintegro():
    raw_text = parse_feed(feed_url)[1]
    start = raw_text.find("R(") + 2
    stop = raw_text.find(")</b>", start)
    raw_reintegro = raw_text[start:stop]
    return raw_reintegro


def complementario():
    raw_text = parse_feed(feed_url)[1]
    start = raw_text.find("C(") + 2
    stop = raw_text.find(")</b>", start)
    raw_complementario = raw_text[start:stop]
    return raw_complementario


def joker():
    raw_text = parse_feed(feed_url)[1]
    start = raw_text.find("J(") + 2
    stop = raw_text.find(")</b>", start)
    raw_joker = raw_text[start:stop]
    return raw_joker


def fecha():
    raw_date = parse_feed(feed_url)[0]
    return raw_date


def is_updated():
    if ultimo_sorteo.count() >= 1:
        ultimo_sorteo_en_db = ultimo_sorteo.distinct("fecha")[0]
        if ultimo_sorteo_en_db == fecha():
            return False
        return True
    else:
        return True


def check_win(numbers, my_numbers):
    lista_de_resultados = []
    for apostante, boleto in my_numbers.items():
        for apuesta in boleto:
            resultado = {}
            aciertos = 0
            numeros_ok = []
            for i in apuesta:
                for j in numbers:
                    if i == j:
                        aciertos += 1
                        numeros_ok.append(i)
                resultado["numeros_ganadores"] = numbers
                resultado["apostante"] = apostante
                resultado["apuesta"] = apuesta
                resultado["aciertos"] = aciertos
                resultado["numeros_acertados"] = numeros_ok
                resultado["fecha"] = fecha()
            coleccion_resultados.insert_one(resultado)
            lista_de_resultados.append(resultado)
    return lista_de_resultados


def main():
    lista_de_resultados = check_win(combinacion(), my_numbers)
    lista_formateada = []

    for resultado in lista_de_resultados:
        lista_formateada.append(
            "Combinación: {}. La apuesta de {}: {} ha tenido {} aciertos.({})".format(
                resultado["numeros_ganadores"],
                resultado["apostante"],
                resultado["apuesta"],
                resultado["aciertos"],
                resultado["numeros_acertados"]
            ))

    # Specifying the from and to addresses
    fromaddr = FROMADDRS
    toaddrs = TOADDRS
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddrs)
    msg['Subject'] = fecha()
    # Writing the message (this message will appear in the email)
    body = fecha() + ":\n\n"
    for array in lista_formateada:
        body += unicode(array, "utf-8") + "\n\n"
    body += "\nREINTEGRO: " + reintegro() + "\n\n"
    body += "COMPLEMENTARIO: " + complementario() + "\n"
    body += "JOKER: " + joker() + "\n"
    msg.attach(MIMEText(body, 'plain', "utf-8"))
    text = msg.as_string()

    # Gmail Login
    username = USERNAME
    password = PASSWORD
    # Sending the mail
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, text)
    server.quit()

    # updates db with last draw's date
    json = {"fecha": fecha()}
    ultimo_sorteo.replace_one({}, json, True)


# # checks date
today = datetime.date.today()
weekday = today.weekday()
if weekday == 3 or weekday == 5:
    while not is_updated():
        time.sleep(600)
    else:
        main()
