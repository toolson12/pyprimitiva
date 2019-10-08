import datetime
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import feedparser
import json
import os
import pymongo
import smtplib
import time

load_dotenv(encoding="utf-8")

FEED_URL = "http://www.loteriasyapuestas.es/es/la-primitiva/resultados/.formatoRSS"

## MongoDB handlers
URI = os.getenv("DB_URI") 
client = pymongo.MongoClient(URI)
db = client["lottery_db"]
coleccion_resultados = db["resultados"]
ultimo_sorteo = db["ultimo_sorteo"]

## Email handlers
USERNAME =  os.getenv("EMAIL_USERNAME") 
PASSWORD = os.getenv("EMAIL_PASSWORD") 
FROMADDRS = os.getenv("EMAIL_FROMADDRS") 
TOADDRS = json.loads(os.getenv("EMAIL_TOADDRS")) 

## Apuestas y apostantes
PARTICIPANTE = os.getenv("PARTICIPANTE")
PARTICIPACIONES = json.loads(os.getenv("PARTICIPACIONES"))

mis_numeros = {
                PARTICIPANTE: PARTICIPACIONES
            } 

def parse_feed(FEED_URL):
    feed = feedparser.parse(FEED_URL)
    raw_date = feed.entries[1]["title"]
    raw_text = feed.entries[1]["description"]
    return raw_date, raw_text


def combinacion():
    raw_text = parse_feed(FEED_URL)[1]
    start = raw_text.find("<b>") + 3
    stop = raw_text.find("</b>")
    raw_numbers = raw_text[start:stop]
    numbers = []
    string_numbers = raw_numbers.split(" - ")
    for number in string_numbers:
        numbers.append(int(number))
    return numbers


def reintegro():
    raw_text = parse_feed(FEED_URL)[1]
    start = raw_text.find("R(") + 2
    stop = raw_text.find(")</b>", start)
    raw_reintegro = raw_text[start:stop]
    return raw_reintegro


def complementario():
    raw_text = parse_feed(FEED_URL)[1]
    start = raw_text.find("C(") + 2
    stop = raw_text.find(")</b>", start)
    raw_complementario = raw_text[start:stop]
    return raw_complementario


def joker():
    raw_text = parse_feed(FEED_URL)[1]
    start = raw_text.find("J(") + 2
    stop = raw_text.find(")</b>", start)
    raw_joker = raw_text[start:stop]
    return raw_joker


def fecha():
    raw_date = parse_feed(FEED_URL)[0]
    return raw_date


def is_updated():
    if ultimo_sorteo.count() >= 1:
        ultimo_sorteo_en_db = ultimo_sorteo.distinct("fecha")[0]
        if ultimo_sorteo_en_db == fecha():
            return False
        return True
    else:
        return True


def check_win(numbers, mis_numeros):
    lista_de_resultados = []
    for apostante, boleto in mis_numeros.items():
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
    lista_de_resultados = check_win(combinacion(), mis_numeros)
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

    # Construcción del email
    fromaddr = FROMADDRS
    toaddrs = TOADDRS
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddrs)
    msg['Subject'] = fecha()    
    body = fecha() + ":\n\n"
    for array in lista_formateada:
        body += str(array) + "\n\n"
    body += "\nREINTEGRO: " + reintegro() + "\n\n"
    body += "COMPLEMENTARIO: " + complementario() + "\n"
    body += "JOKER: " + joker() + "\n"
    msg.attach(MIMEText(body, 'plain', "utf-8"))
    text = msg.as_string()

    # Gmail Login
    username = USERNAME
    password = PASSWORD
    # Envío del email
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
