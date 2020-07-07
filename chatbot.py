"""Dieses Programm empfängt und sendet Informationen aus dem Telegram-chat des bots "prmatestbot". Der code kann für den
fertigen bot genau so verwendet werden, es muss lediglich das token an den neuen bot angepasst werden.

Aktuelle Funktionen: kinder_namen, artikel_zu"""


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
    return dict["viewer"]["value"]#.replace("pm20mets/", "pm20mets/pe/")


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
                            # in Besprechung klären! Diese Zeile ersetzt den Pfad im dictionary der query-Ergebnisse!
                            "access": access_kinder_namen,
                            "layout": None},

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
                          "access": access_artikel_zu}
           }


# general operators
def reply(message):
    replydict = match_pattern(message)
    replydict["qid"] = get_qid(replydict["result"], replydict["find_qid"])
    resultlist = []
    access = "viewer" # replydict["access"]
    for r in get_results(replydict["qid"], replydict["query"])["results"]["bindings"]:
        resultlist.append(replydict["access"](r))
    return ", ".join(resultlist)

# hier wird ein dictionary aus actions ausgegeben, welches um den key "result" ergänzt wird
# regular expression
def match_pattern(message):
    pattern_found = False
    for a in actions.keys():
        if re.compile(actions[a]["regex"]).match(message) is not None:
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


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hallo! Ich bin der Testbot der Gruppe Chatbot aus dem Projekt Pressemappe 20. Jahrhundert! Leider kann ich aktuell nur sagen, wie die Kinder von berühmten Persönlichkeiten heißen und dir Artikel zu Staatsoberhäuptern geben, doch ich lasse hart an mir arbeiten. Viel Spaß!")


starthandler = CommandHandler("start", start)
dispatcher.add_handler(starthandler)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply(update.message.text))


echohandler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echohandler)

updater.start_polling()
