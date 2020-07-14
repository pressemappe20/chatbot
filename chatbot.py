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


# Zugriff auf die gesuchten Werte
def access_kinder_namen(dict):
    return dict["childLabel"]["value"]

def access_artikel_zu(dict):
    return dict["viewer"]["value"].replace("pm20mets/", "pm20mets/pe/")

def access_artikelzahl(dict):
    return dict["workCount"]["value"]

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


qid_suchen = {"person": """SELECT distinct ?item ?itemLabel ?itemDescription WHERE{
            ?item ?label "%s"@de.
            ?item wdt:P31 wd:Q5 .
            ?article schema:about ?item .
            ?article schema:inLanguage "en" .
            ?article schema:isPartOf <https://en.wikipedia.org/>.
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }"""}

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
                           bind(uri(concat('http://dfg-viewer.de/show/?tx_dlf[id]=http://zbw.eu/beta/pm20mets/', ?numStub, 'xx/', ?num, '.xml')) as ?viewer)
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
                               "layout": display_artikelzahl}
           }


# general operators
def reply(message):
    replydict = match_pattern(message)
    replydict["qid"] = get_qid(replydict["result"], replydict["find_qid"])
    resultlist = []
    for r in get_results(replydict["qid"], replydict["query"])["results"]["bindings"]:
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

# emojis
lupe = u"\U0001F50D"
crown = u"\U0001F451"
waving = u"\U0001F44B"

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
    

# add all Commands with dispatcher
starthandler = CommandHandler("start", start)
dispatcher.add_handler(starthandler)

helphandler = CommandHandler("help", help)
dispatcher.add_handler(helphandler)

infohandler = CommandHandler("info", info)
dispatcher.add_handler(infohandler)

dailyspecialhandler = CommandHandler("dailyspecial", dailyspecial)
dispatcher.add_handler(dailyspecialhandler)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply(update.message.text))


echohandler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echohandler)

updater.start_polling()
