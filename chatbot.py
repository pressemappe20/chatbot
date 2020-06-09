"""Dieses Programm empfängt und sendet Informationen aus dem Telegram-chat des bots "prmatestbot". Der code kann für den
fertigen bot genau so verwendet werden, es muss lediglich das token an den neuen bot angepasst werden."""


from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          Filters)
import logging

# Telegram api
updater = Updater(token="1157696049:AAG_ih1xmSQGEckJkAVpHZrGLxbjR9hxOHM", use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="What's up, nerds?")


starthandler = CommandHandler("start", start)
dispatcher.add_handler(starthandler)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply(update.message.text))


echohandler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echohandler)

# general operators
def reply(message):
    regextract = match_pattern(message)
    print("1. Ergebnis regex: %s" % regextract)
    personqid = get_person(regextract)
    print("2. Ergebnis qid: %s" % personqid)
    children = []
    for c in get_names_children(personqid)["results"]["bindings"]:
        children.append(c["childLabel"]["value"])
    for child in children:
        print(child)


# regular expression
def match_pattern(message):
    print(message)
    pattern = re.compile(r'(Wi?e?)\s(heißen)\s(die)\s(Kinder)\s(von)\s(\w+)\s?(\w+)?')
    matches = pattern.finditer(message)
    for match in matches:
        print(match.group(6))
        return match.group(6)


# qid
def get_qid(name, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
    fullquery = query % name
    sparql.setQuery(fullquery)
    sparql.setReturnFormat(JSON)
    searchresults = sparql.query().convert()
    print("qid zwischenergebnis: " + searchresults["results"]["bindings"][0]["item"]["value"].replace("http://www.wikidata.org/entity/", ""))
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
def get_results(query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    print(sparql.query().convert())
    return sparql.query().convert()


def get_names_children(person):
    query = """SELECT ?child ?childLabel 
WHERE
{{
  wd:{person} wdt:P40 ?child .
SERVICE wikibase:label {{bd:serviceParam wikibase:language "en" }}
}}


""".format(person=person)
    return get_results(query)

updater.start_polling()
