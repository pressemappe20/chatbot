"""Dieses Programm empfängt und sendet Informationen aus dem Telegram-chat des bots "prmatestbot". Der code kann für den
fertigen bot genau so verwendet werden, es muss lediglich das token an den neuen bot angepasst werden.

Aktuelle Funktionen: kinder_namen, artikel_zu"""


from telegram import (InlineKeyboardButton,
                      InlineKeyboardMarkup)
from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          Filters)
import logging
import re
from SPARQLWrapper import (SPARQLWrapper,
                           JSON)
from datetime import datetime
import random
import sys

# Sonstiges
def prettydate(date):
    dateobject = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    return dateobject.strftime('%d.%m.%Y')

# emojis
book = u"\U0001F4D6" #Description
cake = u"\U0001F382" # Geburtstag
pin = u"\U0001F4CD" # für Geburtsort und Sterbeort nutzen
skull = u"\U0001F480" # Sterbedatum
knife = u"\U0001F52A"	 # Todesursache
father = u"\U0001F468"  #Vater
mother = u"\U0001F469"  #Mutter
spouse = u"\U0001F46B"  #Ehepartner
camera = u"\U0001F4F8" # Bild/Foto
smiling = u"\U0001F60A"
winking = u"\U0001F609"
lupe = u"\U0001F50D"
crown = u"\U0001F451"
waving = u"\U0001F44B"


# Zugriff auf die gesuchten Werte
def access_kinder_namen(dict):
    return dict["childLabel"]["value"]

def access_artikel_zu(dict):
    return dict["viewer"]["value"]

def access_artikelzahl(dict):
    return dict["workCount"]["value"]

def access_lengthposition(dict):
    return {"position": dict["positionLabel"]["value"],
            "length": dict["length"]["value"],
            "start": prettydate(dict["starttime"]["value"]),
            "end": prettydate(dict["endtime"]["value"])}

def access_generalinformation(dict):
    return {"birthplaceLabel": dict["birthplaceLabel"]["value"],
            "deathplaceLabel": dict["deathplaceLabel"]["value"],
            "birthdate": dict["birthdate"]["value"],
            "deathdate": dict["deathdate"]["value"],
            "deathcauseLabel": dict["deathcauseLabel"]["value"],
            "motherLabel": dict["motherLabel"]["value"],
            "fatherLabel": dict["fatherLabel"]["value"],
            "spouseLabel": dict["spouseLabel"]["value"]}

# Darstellung der Ergebnisse
def display_kinder_namen(resultlist, name):
    if len(resultlist) == 0:
        return "Ich konnte keine Kinder von %s finden. 😢" % name
    elif len(resultlist) == 1:
        return "Die Suche war erfolgreich! %s ist ein Kind von %s!" % (resultlist[0], name)
    else:
        return ("Die Suche war erfolgreich! Hier ist eine Liste der Kinder von %s:\n" % name) + "\n".join(resultlist)

def display_artikel_zu(resultlist, name):
    if len(resultlist) == 0:
        return "Ich konnte keine Artikel zu %s finden. 😢" % name
    else:
        return "Die Suche war erfolgreich! Hier findest du Artikel zu %s:\n%s" % (name, resultlist[0])

def display_artikelzahl(resultlist, name):
    return "Die Suche war erfolgreich! Zu %s gibt es in der Pressemappe %s Artikel." % (name, resultlist[0])

def display_lengthposition(resultlist, name):
    result = resultlist[0]
    return ("Die Suche war erfolgreich! Das habe ich zur Regierungszeit von %s gefunden:\n" % name) +\
           ("\nAmt: %s" % result["position"]) +\
           ("\nBeginn der Amtszeit: %s" % result["start"]) +\
           ("\nEnde der Amtszeit: %s" % result["end"]) +\
           ("\nDauer der Amtszeit: %s Jahre" % int(float(result["length"])))



def display_generalinformation(resultlist, name):
    displaylist = []
    result = resultlist[0]
    if "birthdate" in result.keys():
        displaylist.append("Geboren: %s" % prettydate(result["birthdate"]))
    if "birthplaceLabel" in result.keys():
        displaylist.append("Geburtsort: %s" % result["birthplaceLabel"])
    if "motherLabel" in result.keys():
        displaylist.append("Mutter: %s" % result["motherLabel"])
    if "fatherLabel" in result.keys():
        displaylist.append("Vater: %s" % result["fatherLabel"])
    if "spouseLabel" in result.keys():
        displaylist.append("Gatte/Gattin: %s" % result["spouseLabel"])
    if "deathdate" in result.keys():
        displaylist.append("Gestorben: %s" % prettydate(result["deathdate"]))
    if "deathplaceLabel" in result.keys():
        displaylist.append("Sterbeort: %s" % result["deathplaceLabel"])
    if "deathcauseLabel" in result.keys():
        displaylist.append("Todesursache: %s" % result["deathcauseLabel"])
    return ("Die Suche war erfolgreich! Hier findest du allgemeine Informationen zu %s:\n" % name) + "\n".join(displaylist)

qid_suchen = {"person": """SELECT distinct ?item ?itemLabel ?itemDescription WHERE{
            ?item ?label "%s"@de.
            ?item wdt:P31 wd:Q5 .
            ?article schema:about ?item .
            ?article schema:inLanguage "en" .
            ?article schema:isPartOf <https://en.wikipedia.org/>.
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }""",
             "country": """SELECT distinct ?item ?itemLabel ?itemDescription WHERE{
            ?item ?label "%s"@de.  
            ?item wdt:P31 wd:Q6256 .
            ?article schema:about ?item .
            ?article schema:inLanguage "en" .
            ?article schema:isPartOf <https://en.wikipedia.org/>.	
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
            }"""
             }

actions = {"kinder_namen": {"regex": r'(Wi?e?)\s(heißen)\s(die)\s(Kinder)\s(von)\s(\w+)\s?(\w+)?',
                            "position": 6,
                            "find_qid": qid_suchen["person"],
                            "query": """SELECT ?child ?childLabel
                                 WHERE
                                 {{
                                 wd:{person} wdt:P40 ?child .
                                 SERVICE wikibase:label {{bd:serviceParam wikibase:language "en" }}
                                 }}""",
                            "access": access_kinder_namen,
                            "display":display_kinder_namen},
           "artikel_zu": {"regex": r'(\w+\s?\w+?)\s(Artikel)\s(\w+)\s((\w+)\s?(\w+))',
                          "position": 4,
                          "find_qid": qid_suchen["person"],
                          "query": """PREFIX schema: <http://schema.org/>
                           PREFIX zbwext: <http://zbw.eu/namespaces/zbw-extensions/>
                           select distinct ?pm20 ?viewer ?workCount
                           where {{
                           # get the basic set of persons with "field of activity"
                           # "Staatsoberhaupt" from PM20 endpoint
                           service <http://zbw.eu/beta/sparql/pm20/query> {{
                           ?pm20 zbwext:activity/schema:about "Head of state"@en .
                           bind(strafter(str(?pm20), 'http://purl.org/pressemappe20/folder/') as ?pm20Id)
                           }}
                           wd:{person} wdt:P4293 ?pm20Id .
                           # restrict to items with online accessible articles
                           wd:{person} p:P4293/pq:P5592 ?workCount .
                           filter(?workCount > 0)
                           # viewer link
                           bind(substr(?pm20Id, 4, 4) as ?numStub)
                           bind(substr(?pm20Id, 4, 6) as ?num)
                           bind(uri(concat('http://dfg-viewer.de/show/?tx_dlf[id]=http://zbw.eu/beta/pm20mets/pe/', ?numStub, 'xx/', ?num, '.xml')) as ?viewer)
                           # add labels
                           service wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE], en, de, fr, es, nl, pl, ru" . }}
                           }}
                           """,
                          "access": access_artikel_zu,
                          "display": display_artikel_zu},
           "anzahl_artikel": {"regex": r'(Wie\sviele)\s(Artikel)\s(\w+\s\w+\s?\w+?\s?\w+?)\s(PM20|Pressemappe)\s(\w+)\s(\w+\s?\w+?)',
                               "position": 6,
                               "find_qid": qid_suchen["person"],
                               "query": """PREFIX schema: <http://schema.org/>
                               PREFIX zbwext: <http://zbw.eu/namespaces/zbw-extensions/>
                               select distinct ?item ?itemLabel ?pm20 ?viewer ?workCount
                               where {{
                               # get the basic set of persons with "field of activity"
                               # "Staatsoberhaupt" from PM20 endpoint
                               service <http://zbw.eu/beta/sparql/pm20/query> {{
                               ?pm20 zbwext:activity/schema:about "Head of state"@en .
                               bind(strafter(str(?pm20), 'http://purl.org/pressemappe20/folder/') as ?pm20Id)
                               }}
                               wd:{person} wdt:P4293 ?pm20Id .
                               wd:{person} p:P4293/pq:P5592 ?workCount .
                               filter(?workCount > 0)
                               # viewer link
                               bind(substr(?pm20Id, 4, 4) as ?numStub)
                               bind(substr(?pm20Id, 4, 6) as ?num)
                               bind(uri(concat('http://dfg-viewer.de/show/?tx_dlf[id]=http://zbw.eu/beta/pm20mets/pe/', ?numStub, 'xx/', ?num, '.xml')) as ?viewer)
                               # add labels
                               service wikibase:label {{bd:serviceParam wikibase:language "[AUTO_LANGUAGE], en, de, fr, es, nl, pl, ru" . }}
                               }}""",
                               "access": access_artikelzahl,
                               "display": display_artikelzahl},
           "staatsoberhäupter_von": {"regex": r'(\w+\s\w+)\s(Artikel)\s(\w+)\s(Staatsoberhäuptern|Staatsoberhäupter)\s(\w+)\s(\w+)',
                                     "position": None,
                                     "find_qid": None,
                                     "query": None,
                                     "access": None,
                                     "display": None},
           "regierungszeit": {"regex": r'(\w+)\s(\w+)\s(\w+)\s(\w+\s?\w+?)\s(regiert)',
                                   "position": 4,
                                   "find_qid": qid_suchen["person"],
                                   "query": """
                                   SELECT ?position ?positionLabel ?starttime ?endtime ?length
                                   WHERE 
                                   {{
                                   wd:{person} p:P39 [
                                   ps:P39 ?position ;
                                   pq:P580 ?starttime ;
                                   pq:P582 ?endtime ] .
                                   BIND(?endtime - ?starttime AS ?lengthInDays).
                                   BIND(?lengthInDays/365.2425 AS ?lengthInYears).
                                   BIND(FLOOR(?lengthInYears) AS ?length).
                                   service wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE], de" . }}
                                   }}""",
                                   "access": access_lengthposition,
                                   "display": display_lengthposition},
           "generalinformation": {"regex": r'(\w+\s\w+\s?\w+?)\s(Informationen|Infos)\s(\w+)\s((\w+)\s?(\w+)\s?(\w+))',
                                  "position": 4,
                                  "find_qid": qid_suchen["person"],
                                  "query": """SELECT ?birthdate ?birthplaceLabel ?deathdate ?deathplaceLabel ?deathcauseLabel ?fatherLabel ?motherLabel ?spouseLabel
                                  WHERE
                                  {{
                                  OPTIONAL {{ wd:{person} wdt:P569 ?birthdate . }}
                                  OPTIONAL {{ wd:{person} wdt:P19 ?birthplace . }}
                                  OPTIONAL {{ wd:{person} wdt:P570 ?deathdate . }}
                                  OPTIONAL {{ wd:{person} wdt:P20 ?deathplace . }}
                                  OPTIONAL {{ wd:{person} wdt:P509 ?deathcause . }}
                                  OPTIONAL {{ wd:{person} wdt:P22 ?father . }}
                                  OPTIONAL {{ wd:{person} wdt:P25 ?mother . }}
                                  OPTIONAL {{ wd:{person} wdt:P26 ?spouse . }}
                                  SERVICE wikibase:label {{bd:serviceParam wikibase:language "de" }}
                                  }}""",
                                  "access": access_generalinformation,
                                  "display": display_generalinformation}
           }


# general operators
def reply(message):
    replydict = match_pattern(message)
    replydict["qid"] = get_qid(replydict["result"], replydict["find_qid"])
    resultlist = []
    for r in get_results(replydict["qid"], replydict["query"])["results"]["bindings"]:
        print(r)
        resultlist.append(replydict["access"](r))
    return replydict["display"](resultlist, replydict["result"])

# hier wird ein dictionary aus actions ausgegeben, welches um den key "result" ergänzt wird
# regular expression
def match_pattern(message):
    pattern_found = False
    for a in actions.keys():
        if re.compile(str(actions[a]["regex"])).match(message) is not None:
            pattern_found = True
            key = a
            pattern = re.compile(actions[a]["regex"])
    if pattern_found:
        regextract = actions[key].copy()
        matches = pattern.finditer(message)
        for match in matches:
            regextract["result"] = match.group(actions[key]["position"])
            return regextract


# qid
def get_qid(name, query):
    user_agent = "WDQS-example Python/3.7"
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
    fullquery = query % name
    sparql.setQuery(fullquery)
    sparql.setReturnFormat(JSON)
    searchresults = sparql.query().convert()
    return searchresults["results"]["bindings"][0]["item"]["value"].replace("http://www.wikidata.org/entity/", "")


def get_person(name):
    query = """SELECT distinct ?item ?itemLabel ?itemDescription WHERE{
    ?item ?label "%s"@de.
    ?item wdt:P31 wd:Q5 .
    ?article schema:about ?item .
    ?article schema:inLanguage "en" .
    ?article schema:isPartOf <https://en.wikipedia.org/>.
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }"""
    return get_qid(name, query)


# sparql
def get_results(qid, query):
    user_agent = "WDQS-example Python/3.7"
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
    sparql.setQuery(query.format(person=qid))
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


# Telegram
updater = Updater(token="1311256473:AAGF0N6tjRCO5zIdDwMPOMaE1LfPK3aWies", use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# Erstellen der buttons für die Links
button = [[InlineKeyboardButton(text="Pressemappe 20. Jahrhundert",
                                url="http://webopac0.hwwa.de/PresseMappe20/index.cfm")],
          [InlineKeyboardButton(text="Wikipedia-Artikel zur Pressemappe",
                                url="https://de.wikipedia.org/wiki/Pressearchiv_20._Jahrhundert")]]
show_button = InlineKeyboardMarkup(inline_keyboard=button)


# /start Command
def start(update, context):
   context.bot.send_message(chat_id=update.effective_chat.id,
                            text="Hi! " + waving +
                                 "\nDieser Chatbot wurde erstellt, um Informationen aus der <b>Pressemappe 20. Jahrhundert</b> auszugeben.\n"
                                 "Dieser Chatbot wurde im Rahmen des Projektes “Pressemappe des 20. Jahrhunderts” an der Hochschule der Medien erarbeitet.\n\n"
                                 "Der Bot gibt momentan verschiedene Informationen zu <b>Staatsoberhäuptern</b> aus. Er greift dazu auf die Personendateien in der Pressemappe zu.\n\n"
                                 "Das sind die Commands des Bots:\n\n"
                                 "<b>/info</b>: Wenn du mehr zur Pressemappe erfahren willst, schau hier nach.\n"
                                 "<b>/help</b>: Wenn du Hilfe brauchst, schau bei diesem Command nach. Dort werden die Funktionen des Bots etwas genauer erklärt.\n"
                                 "<b>/dailyspecial</b>: Hier findest du Infos zur Funktion <i>Staatsoberhaupt des Tages</i>\n\n"
                                 "Ansonsten wünschen wir viel Spaß beim Erforschen! " + lupe,
                            parse_mode="HTML")


# /help Command
def help(update, context):
   context.bot.send_message(chat_id=update.effective_chat.id,
                            text="Dieser Chatbot gibt dir Informationen zur <b>Pressemappe des 20. Jahrhunderts</b> (PM20) aus.\n\n"
                                 "Du kannst einfach anfangen, dem Bot Fragen zu stellen, zum Beispiel: <i>Wieviele Kinder hat Joseph Stalin?</i>\n\n"
                                 "Der Chatbot kann momentan etwa 10 verschiedene Fragen und Aufforderungen beantworten:\n\n"
                                 "- Wie heißen die Kinder von <i>{Person}</i>?\n"
                                 "- Wieviele Kinder hat <i>{Person}</i>?\n"
                                 "- Gib mir Artikel über <i>{Person}</i> in PM20\n"
                                 "- Wieviele Artikel gibt es in der PM20 über <i>{Person}</i>?\n"
                                 "- Gib mir ein Bild von <i>{Person}</i>\n"
                                 "- Gib mir Allgemeine Informationen zu <i>{Person}</i>\n"
                                 "- Gib mir weibliche Staatsoberhäupter eines <i>{Landes}</i>\n"
                                 "- Nenn mir Artikel zu Staatsoberhäuptern von <i>{Land}</i>.\n"
                                 "- Mehr als <i>{Anzahl}</i> Artikel in der Pressemappe\n"
                                 "- Wie lange hat <i>{Person}</i> regiert?\n\n"
                                 "Der Bot beschränkt sich bisher auf das Thema <b>Staatsoberhäupter</b>.\n\n"
                                 "Leg los und probiere einfach einige der Fragen aus!",
                            parse_mode="HTML")


# /info Command
def info(update, context):
   context.bot.send_message(chat_id=update.effective_chat.id,
                            text="Informationen zur <b>Pressemappe</b>: \n\n"
                                 "Die Pressemappe umfasst rund 19 Millionen Presseausschnitte, Dokumenten und Bilder zu Verschiedenen sachlichen Themen, Personen und Objekten. "
                                 "Die verschiedenen Bestandteile des Pressearchivs wurden teilweise digitalisiert und insbesondere die Personenmappen sind fast vollständig online abrufbar.\n\n"
                                 "Im Oktober 2019 wurden in einem ersten Schritt die Metadaten zu etwa 5000 Personendossiers der Pressemappe an Wikidata weitergegeben und dort aufgenommen.\n\n"
                                 "Der Chatbot greift auf das Thema <b>Staatsoberhäupter</b> zurück, das momentan 218 Datensätze umfasst.\n\n"
                                 "Mehr zur ausführlichen Geschichte und detailierten Infos findest du auf der Startseite der <b>Pressemappe</b> und auf dem <b>Wikipedia-Artikel</b>"
                                 " zur Pressemappe.",
                            parse_mode="HTML",
                            reply_markup=show_button)


# /dailyspecial Command
def dailyspecial(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Wir haben die Funktion “Staatsoberhaupt des Tages” für dich erstellt!\n\n"
                                  "Damit bekommst du jeden Tag grundlegende Informationen zu einem beliebig gewählten Staatsoberhaupt aus der Pressemappe. "
                                  "So bekommst du jeden Tag deine Dosis an Informationen zu verschiedenen Königen, Königinnen "
                                  "und anderen Staatsoberhäuptern! " + crown,
                             parse_mode="HTML")

    
# Daily Special Funktion
endpoint_url = "https://query.wikidata.org/sparql"

def get_results_ds(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # print(sparql.query().convert())
    return sparql.query().convert()


def get_random_staatsoberhaupt(endpoint_url):
    query = """
       PREFIX schema: <http://schema.org/>
       PREFIX zbwext: <http://zbw.eu/namespaces/zbw-extensions/>
       SELECT DISTINCT ?item ?itemLabel ?itemDescription ?pm20 ?viewer ?workCount ?birthdate ?birthplaceLabel ?deathdate ?deathplaceLabel ?deathcauseLabel ?fatherLabel ?motherLabel ?spouseLabel ?pic
       where {
       service <http://zbw.eu/beta/sparql/pm20/query> {
        ?pm20 zbwext:activity/schema:about "Head of state"@en .
        bind(strafter(str(?pm20), 'http://purl.org/pressemappe20/folder/') as ?pm20Id)
      }
       ?item wdt:P4293 ?pm20Id .
         OPTIONAL { ?item wdt:P569 ?birthdate . }
         OPTIONAL { ?item wdt:P19 ?birthplace . }
         OPTIONAL { ?item wdt:P570 ?deathdate . }
         OPTIONAL { ?item wdt:P20 ?deathplace . }
         OPTIONAL { ?item wdt:P509 ?deathcause . }
         OPTIONAL { ?item wdt:P22 ?father . }
         OPTIONAL { ?item wdt:P25 ?mother . }
         OPTIONAL { ?item wdt:P26 ?spouse . }
         OPTIONAL { ?item wdt:P18 ?pic . }
         SERVICE wikibase:label {bd:serviceParam wikibase:language "en" }
        ?item p:P4293/pq:P5592 ?workCount .
      filter(?workCount > 0)
      bind(substr(?pm20Id, 4, 4) as ?numStub)
      bind(substr(?pm20Id, 4, 6) as ?num)
      bind(uri(concat('http://dfg-viewer.de/show/?tx_dlf[id]=http://zbw.eu/beta/pm20mets/pe/', ?numStub, 'xx/', ?num, '.xml')) as ?viewer)
      service wikibase:label { bd:serviceParam wikibase:language "de" . }
         }
        """
    return (get_results_ds(endpoint_url, query))

# ergebnisse in variable speichern
resultjson = get_random_staatsoberhaupt(endpoint_url)

def daily_special():
    staatsoberhaupt_counter = len(resultjson['results']['bindings'])
    random_index = random.randint(0, staatsoberhaupt_counter - 1)

    def daily_staatsoberhaupt():
        name = resultjson['results']['bindings'][random_index]['itemLabel']['value']
        return name

    def daily_description():
        description = resultjson['results']['bindings'][random_index]['itemDescription']['value']
        return description

    def daily_birthdate():
        birthdate = datetime.strptime(resultjson['results']['bindings'][random_index]['birthdate']['value'], '%Y-%m-%dT%H:%M:%SZ')
        return birthdate.strftime('%d.%m.%Y')

    def daily_birthplace():
        birthplace = resultjson['results']['bindings'][random_index]['birthplaceLabel']['value']
        if birthplace.startswith('Q') == True:
            return None
        else:
            return birthplace

    def daily_deathdate():
        deathdate = datetime.strptime(resultjson['results']['bindings'][random_index]['deathdate']['value'], '%Y-%m-%dT%H:%M:%SZ')
        return deathdate.strftime('%d.%m.%Y')

    def daily_deathplace():
        deathplace = resultjson['results']['bindings'][random_index]['deathplaceLabel']['value']
        if deathplace.startswith('Q') == True:
            return None
        else:
            return deathplace

    def daily_mother():
        mother = resultjson['results']['bindings'][random_index]['motherLabel']['value']
        if mother.startswith('Q') == True:
            return None
        else:
            return mother

    def daily_father():
        father = resultjson['results']['bindings'][random_index]['fatherLabel']['value']
        if father.startswith('Q') == True:
            return None
        else:
            return father

    def daily_spouse():
        spouse = resultjson['results']['bindings'][random_index]['spouseLabel']['value']
        if spouse.startswith('Q') == True:
            return None
        else:
            return spouse

    def daily_pic():
        pic = resultjson['results']['bindings'][random_index]['pic']['value']
        return pic

    # Durch den Multiline String muss das leider so komisch eingerückt werden, ansonsten sieht die Ausgabe in Telegram...nicht gut aus.
    message = """
Das Staatsoberhaupt des Tages ist: <b>{name}</b>\n\n
{e0} <b>Beschreibung:</b> {description}
{e1} <b>Geburtsdatum:</b> {bdate}
{e2} <b>Geburtsort:</b> {bplace}
{e3} <b>Sterbedatum:</b> {ddate}
{e4} <b>Sterbeort:</b> {dplace}
{e5} <b>Mutter:</b> {mother}
{e6} <b>Vater:</b> {father}
{e7} <b>Ehepartner:</b> {spouse}\n
Falls das Bild der Person nicht angezeigt wird, <a href="{pic}">{e8} klicke hier!</a>\n\n
Das war das Staatsoberhaupt des Tages! Jetzt hast du wieder etwas neues erfahren!\n
    """.format(e0=book, e1=cake, e2=pin, e3=skull, e4=pin, e5=mother, e6=father, e7=spouse, e8=camera,
        name=daily_staatsoberhaupt(),
        description=daily_description(),
        bdate=daily_birthdate(),
        bplace=daily_birthplace(),
        ddate=daily_deathdate(),
        dplace=daily_deathplace(),
        mother=daily_mother(),
        father=daily_father(),
        spouse=daily_spouse(),
        pic=daily_pic())
    return message


# speichert chat_id aller Nutzer, die den Command /abo aufrufen
abolist = []

def abo(update, context):
    id = update.message.chat_id
    if id in abolist:
        answer = "Du hast das Daily Special schon abonniert! " + winking
    else:
        answer = "Super! Jetzt hast du das Daily Special abonniert und bekommst jeden Tag eine Nachricht zu einem " \
                 "beliebigen Staatsoberhaupt aus der Pressemappe! " + smiling
        abolist.append(id)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=answer,
                             parse_mode="HTML")
    return abolist


# Job Queue erstellen (ist an Updater gebunden!)
j = updater.job_queue

def send_ds(context):
    for i in abolist:
        context.bot.send_message(chat_id=i, text=daily_special(), parse_mode="HTML")


# run job queue, muss noch verändert werden, für Testzwecke alle 30 sek
job_minute = j.run_repeating(send_ds, interval=30, first=0)

#job_ds = j.run_daily(send_ds)


# add all Commands with dispatcher
starthandler = CommandHandler("start", start)
dispatcher.add_handler(starthandler)

helphandler = CommandHandler("help", help)
dispatcher.add_handler(helphandler)

infohandler = CommandHandler("info", info)
dispatcher.add_handler(infohandler)

dailyspecialhandler = CommandHandler("dailyspecial", dailyspecial)
dispatcher.add_handler(dailyspecialhandler)

abohandler = CommandHandler("abo", abo)
dispatcher.add_handler(abohandler)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply(update.message.text))

echohandler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echohandler)

updater.start_polling()
