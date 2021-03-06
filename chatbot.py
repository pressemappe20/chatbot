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


def is_qid(text):
    if re.compile(r'(Q\d+)').match(text) is not None:
        return ""
    else:
        return text


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
thinking = u"\U0001F914"
person = u"\U0001F464"


# Zugriff auf die gesuchten Werte
def access_kinder_namen(dict):
    return dict["childLabel"]["value"]


def access_artikel_zu(dict):
    return dict["viewer"]["value"]


def access_artikelzahl(dict):
    return dict["workCount"]["value"]


def access_so_land(dict):
    return {"headofcountry": dict['itemLabel']['value'],
            "pressemappe": dict['pm20']['value'],
            "viewer": dict['viewer']['value']}

def access_w_so_land(dict):
    return {"headofcountry": dict['itemLabel']['value'],
            "pressemappe": dict['pm20']['value'],
            "viewer": dict['viewer']['value']}


def access_lengthposition(dict):
    return {"position": dict["positionLabel"]["value"],
            "length": dict["length"]["value"],
            "start": prettydate(dict["starttime"]["value"]),
            "end": prettydate(dict["endtime"]["value"])}


def access_generalinformation(dict):
    return {"birthplaceLabel": is_qid(dict["birthplaceLabel"]["value"]),
            "deathplaceLabel": is_qid(dict["deathplaceLabel"]["value"]),
            "birthdate": dict["birthdate"]["value"],
            "deathdate": dict["deathdate"]["value"],
            "deathcauseLabel": is_qid(dict["deathcauseLabel"]["value"]),
            "motherLabel": is_qid(dict["motherLabel"]["value"]),
            "fatherLabel": is_qid(dict["fatherLabel"]["value"]),
            "spouseLabel": is_qid(dict["spouseLabel"]["value"])}


def access_picture(dict):
    return dict["pic"]["value"]


def access_articles_ab(dict):
    return {"name": dict["itemLabel"]["value"],
            "pressemappe": dict["pm20"]["value"],
            "viewer": dict["viewer"]["value"],
            "works": dict["workCount"]["value"]}


def access_found_cat(dict):
    return "In honor of Mrs. Chippy."


# Darstellung der Ergebnisse
def display_kinder_namen(resultlist, name):
    if len(resultlist) == 0:
        return "Ich konnte keine Kinder von %s finden. 😢" % name
    elif len(resultlist) == 1:
        return "Die Suche war erfolgreich! <b>%s</b> ist ein Kind von <b>%s</b>!" % (resultlist[0], name)
    else:
        return ("Die Suche war erfolgreich! Hier ist eine Liste der <b>Kinder von %s:</b>\n\n" % name) + "\n".join(resultlist)

def display_artikel_zu(resultlist, name):
    if len(resultlist) == 0:
        return "Ich konnte keine Artikel zu <b>%s</b> finden. 😢" % name
    else:
        return """Die Suche war erfolgreich! <a href="{link}">Hier</a> findest du Artikel zu <b>{name}</b>.""".format(name=name, link=resultlist[0])

def display_artikelzahl(resultlist, name):
    return "Die Suche war erfolgreich! Zu <b>%s</b> gibt es in der Pressemappe <b>%s</b> Artikel." % (name, resultlist[0])

def display_so_land(resultlist, country):
    if len(resultlist) == 0:
        return "Ich konnte keine Staatsoberhäupter von %s finden. 😢" % country
    elif len(resultlist) == 1:
        return "Die Suche war erfolgreich! <b>%s</b> ist ein Staatsoberhaupt von <b>%s</b>!" % (resultlist[0], country)
    else:
        displaylist = []
        for r in resultlist:
            displaylist.append("""<b>{name}</b>\n<a href="{plink}">Pressemappe-Link</a>\n<a href="{vlink}">Viewer-Link</a>""".format(name=r["headofcountry"], plink=r["pressemappe"], vlink=r["viewer"]))
        return ("Die Suche war erfolgreich! Hier ist eine Liste von Staatsoberhäuptern von <b>%s</b>:\n\n" % country) + "\n\n".join(displaylist)

def display_w_so_land(resultlist, country):
    if len(resultlist) == 0:
        return "Ich konnte keine weiblichen Staatsoberhäupter von <b>%s</b> finden. 😢" % country
    elif len(resultlist) == 1:
        return ("Die Suche war erfolgreich! Ich habe ein weibliches Staatsoberhaupt von <b>%s</b> gefunden:\n\n" % country) +\
               ("""<b>{name}</b>\n<a href="{plink}">Pressemappe-Link</a>\n<a href="{vlink}">Viewer-Link</a>""".format(name=resultlist[0]["headofcountry"], plink=resultlist[0]["pressemappe"], vlink=resultlist[0]["viewer"]))
    else:
        displaylist = []
        for r in resultlist:
            displaylist.append("""<b>{name}</b>\n<a href="{plink}">Pressemappe-Link</a>\n<a href="{vlink}">Viewer-Link</a>""".format(name=r["headofcountry"], plink=r["pressemappe"], vlink=r["viewer"]))
        return ("Die Suche war erfolgreich! Hier ist eine Liste von weiblichen Staatsoberhäuptern von <b>%s</b>:\n\n" % country) + "\n\n".join(displaylist)

def display_lengthposition(resultlist, name):
    result = resultlist[0]
    return ("Die Suche war erfolgreich! Das habe ich zur Regierungszeit von <b>%s</b> gefunden:\n" % name) +\
           ("\n<b>Amt:</b> %s" % result["position"]) +\
           ("\n<b>Beginn der Amtszeit</b>: %s" % result["start"]) +\
           ("\n<b>Ende der Amtszeit</b>: %s" % result["end"]) +\
           ("\n<b>Dauer der Amtszeit</b>: %s Jahre" % int(float(result["length"])))

def display_generalinformation(resultlist, name):
    displaylist = []
    result = resultlist[0]
    if "birthdate" in result.keys():
        displaylist.append("\n" + cake + " <b>Geboren</b>: %s" % prettydate(result["birthdate"]))
    if "birthplaceLabel" in result.keys():
        if len(result["birthplaceLabel"]) > 0:
            displaylist.append(pin + " <b>Geburtsort</b>: %s" % result["birthplaceLabel"])
    if "motherLabel" in result.keys():
        if len(result["motherLabel"]) > 0:
            displaylist.append(mother + " <b>Mutter</b>: %s" % result["motherLabel"])
    if "fatherLabel" in result.keys():
        if len(result["fatherLabel"]) > 0:
            displaylist.append(father + " <b>Vater</b>: %s" % result["fatherLabel"])
    if "spouseLabel" in result.keys():
        if len(result["spouseLabel"]) > 0:
            displaylist.append(spouse + " <b>Gatte/Gattin</b>: %s" % result["spouseLabel"])
    if "deathdate" in result.keys():
        displaylist.append(skull + " <b>Gestorben</b>: %s" % prettydate(result["deathdate"]))
    if "deathplaceLabel" in result.keys():
        if len(result["deathplaceLabel"]) > 0:
            displaylist.append(pin + " <b>Sterbeort</b>: %s" % result["deathplaceLabel"])
    if "deathcauseLabel" in result.keys():
        if len(result["deathcauseLabel"]) > 0:
            displaylist.append(knife + " <b>Todesursache</b>: %s" % result["deathcauseLabel"])
    return ("Die Suche war erfolgreich! Hier findest du allgemeine Informationen zu <b>%s</b>:\n" % name) + "\n".join(displaylist)

def display_picture(resultlist, name):
    if len(resultlist) == 0:
        return "Ich habe heute leider kein Foto (von %s) für dich. 😢" % name
    else:
        return """<a href="{link}">{person}</a> Hier ist ein Bild von <b>{name}</b>:""".format(person=person, link=resultlist[0], name=name)

def display_articles_ab(resultlist, number):
    displaylist = []
    counter = 0
    resultlist.reverse()
    for r in resultlist:
        counter += 1
        displaylist.append("""{rank}. <b>{person}</b> ({number} Artikel)\n<a href="{plink}">Pressemappe-Link</a>\n<a href="{dlink}">DFG-Viewer</a>""".format(rank=counter,
                                                                                                                                                      person=r["name"],
                                                                                                                                                      number=r["works"],
                                                                                                                                                      plink=r["pressemappe"],
                                                                                                                                                      dlink=r["viewer"]))
    return ("Die Suche war erfolgreich! Folgende Einträge besitzen über %s Artikel:\n\n" % number) + "\n\n".join(displaylist)

def display_fehler(resultlist, name):
    return "Das habe ich leider nicht verstanden. 😢\nUnter <b>/help</b> findest du meine Funktionen."

qid_suchen = {"person": """PREFIX schema: <http://schema.org/>
PREFIX zbwext: <http://zbw.eu/namespaces/zbw-extensions/>
SELECT distinct ?item ?itemLabel ?itemDescription WHERE{
            ?item ?label "%s"@de.
            ?item wdt:P31 wd:Q5 .
            service <http://zbw.eu/beta/sparql/pm20/query> {{
                                                 ?pm20 zbwext:activity/schema:about "Head of state"@en .
                                                 bind(strafter(str(?pm20), 'http://purl.org/pressemappe20/folder/') as ?pm20Id)
                                                 }}
                                                 ?item wdt:P4293 ?pm20Id .
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
            }""",
             "cat": """SELECT DISTINCT ?item ?itemLabel ?itemDescription WHERE {
            ?item ?label "%s"@de;
            wdt:P31 wd:Q146.
            ?article schema:about ?item;
            schema:inLanguage "en";
            schema:isPartOf <https://en.wikipedia.org/>.
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }"""}

actions = {"kinder_namen": {"regex": r'(Wi?e?)\s(heißen)\s(die)\s(Kinder)\s(von)\s(\w+\s?\w+\s?\w+\s?\w+\s?\w+\s?\w+?)',
                            "position": 6,
                            "find_qid": qid_suchen["person"],
                            "query": """SELECT ?child ?childLabel
                                 WHERE
                                 {{
                                 wd:{qid} wdt:P40 ?child .
                                 SERVICE wikibase:label {{bd:serviceParam wikibase:language "en" }}
                                 }}""",
                            "access": access_kinder_namen,
                            "display":display_kinder_namen},
           "artikel_zu": {"regex": r'(\w+\s?\w+?)\s(Artikel)\s(\w+)\s(\w+\s?\w+\s?\w+\s?\w+\s?\w+\s?\w+?)',
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
                           wd:{qid} wdt:P4293 ?pm20Id .
                           # restrict to items with online accessible articles
                           wd:{qid} p:P4293/pq:P5592 ?workCount .
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
           "anzahl_artikel": {"regex": r'(Wie\s?viele)\s(Artikel)\s(\w+\s\w+\s?\w+?\s?\w+?)\s(PM20|Pressemappe)\s(\w+)\s(\w+\s?\w+\s?\w+\s?\w+\s?\w+\s?\w+?)',
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
                               wd:{qid} wdt:P4293 ?pm20Id .
                               wd:{qid} p:P4293/pq:P5592 ?workCount .
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
           "staatsoberhaeupter_von": {"regex": r'(\w+\s\w+)\s(Artikel)\s(\w+)\s(Staatsoberhäuptern|Staatsoberhäupter)\s(\w+)\s(\w+\s?\w+\s?\w+\s?\w+\s?\w+\s?\w+?)',
                                     "position": 6,
                                     "find_qid": qid_suchen["country"],
                                     "query": """PREFIX schema: <http://schema.org/>
                                                 PREFIX zbwext: <http://zbw.eu/namespaces/zbw-extensions/>
                                                 select distinct ?item ?itemLabel ?pm20 ?viewer ?workCount
                                                 where {{
                                                 service <http://zbw.eu/beta/sparql/pm20/query> {{
                                                 ?pm20 zbwext:activity/schema:about "Head of state"@en .
                                                 bind(strafter(str(?pm20), 'http://purl.org/pressemappe20/folder/') as ?pm20Id)
                                                 }}
                                                 ?item wdt:P4293 ?pm20Id .
                                                 ?item wdt:P27 wd:{qid}.
                                                 ?item p:P4293/pq:P5592 ?workCount .
                                                 filter(?workCount > 0)
                                                 bind(substr(?pm20Id, 4, 4) as ?numStub)
                                                 bind(substr(?pm20Id, 4, 6) as ?num)
                                                 bind(uri(concat('http://dfg-viewer.de/show/?tx_dlf[id]=http://zbw.eu/beta/pm20mets/pe/', ?numStub, 'xx/', ?num, '.xml')) as ?viewer)
                                                 service wikibase:label {{ bd:serviceParam wikibase:language "de" . }}
                                                 }}
                                                 order by ?itemLabel""",
                                     "access": access_so_land,
                                     "display": display_so_land},
           "w_staatsoberhaeupter": {"regex": r'(\w+\s?\w+\s?\w+?\s?\w+?)\s(weibliche|weiblichen)\s(Staatsoberhäupter|Staatsoberhäuptern)\s(von)\s(\w+\s?\w+\s?\w+\s?\w+\s?\w+\s?\w+?)',
                                    "position": 5,
                                    "find_qid": qid_suchen["country"],
                                    "query": """PREFIX schema: <http://schema.org/>
                                    PREFIX zbwext: <http://zbw.eu/namespaces/zbw-extensions/>
                                    select distinct ?item ?itemLabel ?pm20 ?viewer ?workCount
                                    where {{
                                    service <http://zbw.eu/beta/sparql/pm20/query> {{
                                    ?pm20 zbwext:activity/schema:about "Head of state"@en .
                                    bind(strafter(str(?pm20), 'http://purl.org/pressemappe20/folder/') as ?pm20Id)
                                    }}
                                    ?item wdt:P4293 ?pm20Id .
                                    ?item p:P4293/pq:P5592 ?workCount .
                                    filter(?workCount > 0)
                                    bind(substr(?pm20Id, 4, 4) as ?numStub)
                                    bind(substr(?pm20Id, 4, 6) as ?num)
                                    bind(uri(concat('http://dfg-viewer.de/show/?tx_dlf[id]=http://zbw.eu/beta/pm20mets/pe/', ?numStub, 'xx/', ?num, '.xml')) as ?viewer)
                                    service wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE], de" . }}
                                    ?item wdt:P21 wd:Q6581072 .
                                    ?item wdt:P27 wd:{qid}.
                                    }}""",
                                    "access": access_w_so_land,
                                    "display": display_w_so_land},
           "regierungszeit": {"regex": r'(\w+)\s(\w+)\s(\w+)\s(\w+\s?\w+\s?\w+\s?\w+\s?\w+\s?\w+?)\s(regiert)',
                                   "position": 4,
                                   "find_qid": qid_suchen["person"],
                                   "query": """
                                   SELECT ?position ?positionLabel ?starttime ?endtime ?length
                                   WHERE 
                                   {{
                                   wd:{qid} p:P39 [
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
           "generalinformation": {"regex": r'(\w+\s\w+\s?\w+?)\s(Informationen|Infos)\s(\w+)\s(\w+\s?\w+\s?\w+\s?\w+\s?\w+\s?\w+?)',
                                  "position": 4,
                                  "find_qid": qid_suchen["person"],
                                  "query": """SELECT ?birthdate ?birthplaceLabel ?deathdate ?deathplaceLabel ?deathcauseLabel ?fatherLabel ?motherLabel ?spouseLabel
                                  WHERE
                                  {{
                                  OPTIONAL {{ wd:{qid} wdt:P569 ?birthdate . }}
                                  OPTIONAL {{ wd:{qid} wdt:P19 ?birthplace . }}
                                  OPTIONAL {{ wd:{qid} wdt:P570 ?deathdate . }}
                                  OPTIONAL {{ wd:{qid} wdt:P20 ?deathplace . }}
                                  OPTIONAL {{ wd:{qid} wdt:P509 ?deathcause . }}
                                  OPTIONAL {{ wd:{qid} wdt:P22 ?father . }}
                                  OPTIONAL {{ wd:{qid} wdt:P25 ?mother . }}
                                  OPTIONAL {{ wd:{qid} wdt:P26 ?spouse . }}
                                  SERVICE wikibase:label {{bd:serviceParam wikibase:language "de" }}
                                  }}""",
                                  "access": access_generalinformation,
                                  "display": display_generalinformation},
           "picture": {"regex": r'(\w+)\s(\w+)\s(Bilder|ein Bild|Fotos|ein Foto)\s(\w+)\s(\w+\s?\w+\s?\w+\s?\w+\s?\w+\s?\w+?)',
                       "position": 5,
                       "find_qid": qid_suchen["person"],
                       "query": """SELECT ?pic
                       WHERE
                       {{
                       wd:{qid}  wdt:P18 ?pic
                       }}
                       """,
                       "access": access_picture,
                       "display": display_picture},
           "articles_above": {"regex": r'(\w+\s?\w+?)\s(Staatsoberhäupter|Staatsoberhäuptern)\s(\w+\s\w+\s\w+\s?\w+?)\s(\d+)\s(Artikel|Artikeln)\s(\w+\s\w+)\s(Pressemappe|PM20)',
                              "position": 4,
                              "find_qid": None,
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
                              ?item wdt:P4293 ?pm20Id .
                              #
                              # restrict to items with online accessible articles
                              ?item p:P4293/pq:P5592 ?workCount .
                              filter(?workCount > {qid})
                              # viewer link
                              bind(substr(?pm20Id, 4, 4) as ?numStub)
                              bind(substr(?pm20Id, 4, 6) as ?num)
                              bind(uri(concat('http://dfg-viewer.de/show/?tx_dlf[id]=http://zbw.eu/beta/pm20mets/pe/', ?numStub, 'xx/', ?num, '.xml')) as ?viewer)
                              # add labels
                              service wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE], en, de, fr, es, nl, pl, ru" . }}
                              }}
                              order by ?workCount""",
                              "access": access_articles_ab,
                              "display": display_articles_ab},
           "found_cat": {"regex": None,
                         "position": None,
                         "find_qid": qid_suchen["cat"],
                         "query": """SELECT ?deathLabel
                         WHERE 
                         {{
                         wd:{qid} wdt:P509 ?death.
                         SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],de". }}
                         }}""",
                         "access": access_found_cat,
                         "display": display_fehler}
           }


# general operators
def reply(message):
    replydict = match_pattern(message)
    if replydict["find_qid"] is not None:
        replydict["qid"] = get_qid(replydict["result"], replydict["find_qid"])
    else:
        replydict["qid"] = replydict["result"]
    if replydict["qid"] is False:
        return "Leider habe ich zu deiner Anfrage keinen passenden Datensatz finden können. 😢"
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
    else:
        regextract = actions["found_cat"].copy()
        regextract["result"] = "Mrs. Chippy"
        return regextract


# qid
def get_qid(name, query):
    user_agent = "WDQS-example Python/3.7"
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
    fullquery = query % name
    sparql.setQuery(fullquery)
    sparql.setReturnFormat(JSON)
    searchresults = sparql.query().convert()
    try:
        return searchresults["results"]["bindings"][0]["item"]["value"].replace("http://www.wikidata.org/entity/", "")
    except IndexError:
        return False


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
    sparql.setQuery(query.format(qid=qid))
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
                                 "<b>/dailyspecial</b>: Hier findest du Infos zur <em>Daily Special</em> Funktion.\n"
                                 "<b>/abo</b>: Abonnieren der <em>Daily Special</em> Funktion.\n"
                                 "<b>/abo_stop</b>: De-Abonnieren der <em>Daily Special</em> Funktion.\n\n"
                                 "Ansonsten wünschen wir viel Spaß beim Erforschen! " + lupe,
                            parse_mode="HTML")


# /help Command
def help(update, context):
   context.bot.send_message(chat_id=update.effective_chat.id,
                            text="Dieser Chatbot gibt dir Informationen zur <b>Pressemappe des 20. Jahrhunderts</b> (PM20) aus.\n\n"
                                 "Du kannst einfach anfangen, dem Bot Fragen zu stellen, zum Beispiel: <i>Wieviele Kinder hat Joseph Stalin?</i>\n\n"
                                 "Der Chatbot kann momentan etwa 10 verschiedene Fragen und Aufforderungen beantworten:\n\n"
                                 "- Gib mir Infos zu <i>{Staatsoberhaupt}</i>.\n"
                                 "- Gib mir Artikel zu <i>{Staatsoberhaupt}</i>.\n"
                                 "- Wie viele Artikel gibt es in der Pressemappe zu <i>{Staatsoberhaupt}</i>?\n"
                                 "- Wie heißen die Kinder von <i>{Staatsoberhaupt}</i>?\n"
                                 "- Wie lange hat <i>{Staatsoberhaupt}</i> regiert?\n"
                                 "- Gib mir ein Bild von <i>{Staatsoberhaupt}</i>.\n"
                                 "- Gib mir Artikel zu Staatsoberhäupter von <i>{Land}</i>.\n"
                                 "- Gib mir Artikel zu weiblichen Staatsoberhäuptern von <i>{Land}</i>.\n"
                                 "- Welche Staatsoberhäupter besitzen mehr als <i>{Zahl}</i> Artikel in der Pressemappe?\n"
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
                             text="Wir haben die Funktion <em>Daily Special</em> für dich erstellt!\n\n"
                                  "Damit bekommst du jeden Tag grundlegende Informationen zu einem beliebig gewählten Staatsoberhaupt aus der Pressemappe. "
                                  "So bekommst du jeden Tag deine Dosis an Informationen zu verschiedenen Königen, Königinnen "
                                  "und anderen Staatsoberhäuptern! " + crown + "\n\nDu kannst die Funktion mit dem Command <b>/abo</b> abonnieren, "
                                  "mit dem Command <b>/abo_stop</b> kannst du dich wieder abmelden.",
                             parse_mode="HTML")

# filtert alle Commands, die nicht gespeichert wurden
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Diesen Command gibt es leider nicht. " + thinking +
                             "\nMomentan gibt es folgende Befehle:\n\n"
                             "<b>/info</b>: Wenn du mehr zur Pressemappe erfahren willst, schau hier nach.\n"
                             "<b>/help</b>: Wenn du Hilfe brauchst, schau bei diesem Command nach. Dort werden die Funktionen des Bots etwas genauer erklärt.\n"
                             "<b>/dailyspecial</b>: Hier findest du Infos zur Funktion <i>Staatsoberhaupt des Tages</i>\n\n"
                             "Wahrscheinlich hast du einen hiervon gemeint!",
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
        if is_qid(birthplace) == "":
            return None
        else:
            return birthplace

    def daily_deathdate():
        deathdate = datetime.strptime(resultjson['results']['bindings'][random_index]['deathdate']['value'], '%Y-%m-%dT%H:%M:%SZ')
        return deathdate.strftime('%d.%m.%Y')

    def daily_deathplace():
        deathplace = resultjson['results']['bindings'][random_index]['deathplaceLabel']['value']
        if is_qid(deathplace) == "":
            return None
        else:
            return deathplace

    def daily_mother():
        mother = resultjson['results']['bindings'][random_index]['motherLabel']['value']
        if is_qid(mother) == "":
            return None
        else:
            return mother

    def daily_father():
        father = resultjson['results']['bindings'][random_index]['fatherLabel']['value']
        if is_qid(father) == "":
            return None
        else:
            return father

    def daily_spouse():
        spouse = resultjson['results']['bindings'][random_index]['spouseLabel']['value']
        if is_qid(spouse) == "":
            return None
        else:
            return spouse

    def daily_pic():
        pic = resultjson['results']['bindings'][random_index]['pic']['value']
        return pic

    # Durch den Multiline String muss das leider so komisch eingerückt werden, ansonsten sieht die Ausgabe in Telegram...nicht gut aus.
    messagelist = []
    messagelist.append("Das Staatsoberhaupt des Tages ist: <b>{name}</b>\n".format(name=daily_staatsoberhaupt()))
    if daily_description() is not None:
        messagelist.append("{e0} <b>Beschreibung:</b> {description}".format(e0=book, description=daily_description()))
    if daily_birthdate() is not None:
        messagelist.append("{e1} <b>Geburtsdatum:</b> {bdate}".format(e1=cake, bdate=daily_birthdate()))
    if daily_birthplace() is not None:
        messagelist.append("{e2} <b>Geburtsort:</b> {bplace}".format(e2=pin, bplace=daily_birthplace()))
    if daily_deathdate() is not None:
        messagelist.append("{e3} <b>Sterbedatum:</b> {ddate}".format(e3=skull, ddate=daily_deathdate()))
    if daily_deathplace() is not None:
        messagelist.append("{e4} <b>Sterbeort:</b> {dplace}".format(e4=pin, dplace=daily_deathplace()))
    if daily_mother() is not None:
        messagelist.append("{e5} <b>Mutter:</b> {mother}".format(e5=mother, mother=daily_mother()))
    if daily_father() is not None:
        messagelist.append("{e6} <b>Vater:</b> {father}".format(e6=father, father=daily_father()))
    if daily_spouse() is not None:
        messagelist.append("{e7} <b>Ehepartner*in:</b> {spouse}\n".format(e7=spouse, spouse=daily_spouse()))

    messagelist.append("""Falls das Bild der Person nicht angezeigt wird, <a href="{pic}">{e8} klicke hier!</a>\n\n
Das war das Staatsoberhaupt des Tages! Jetzt hast du wieder etwas neues erfahren!\n""".format(e8=camera, pic=daily_pic()))
    return "\n".join(messagelist)

# speichert chat_id aller Nutzer, die den Command /abo aufrufen
abolist = []

def abo(update, context):
    id = update.message.chat_id
    if id in abolist:
        answer = "Du hast das <b>Daily Special</b> schon abonniert! Wenn du dich abmelden willst, dann benutze den Command <b>/abo_stop.</b> " + winking
    else:
        answer = "Super! Jetzt hast du das <b>Daily Special</b> abonniert und bekommst jeden Tag eine Nachricht zu einem " \
                 "beliebigen Staatsoberhaupt aus der Pressemappe! " + smiling + "\n\nWenn du keine Nachrichten mehr bekommen möchtest, " \
                 "melde dich einfach mit dem Command <b>/abo_stop</b> vom <b>Daily Special</b> ab."
        abolist.append(id)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=answer,
                             parse_mode="HTML")
    return abolist


# entfernt chat_id wieder
def abo_stop(update, context):
    id = update.message.chat_id
    if id in abolist:
        abolist.remove(id)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Du hast dich jetzt vom <b>Daily Special</b> abgemeldet. Wenn du die Funktion wieder abonnieren möchtest, "
                                      "benutze den Command /abo. " + smiling,
                                 parse_mode="HTML")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Du hast das <b>Daily Special</b> nicht abonniert, deswegen kannst du dich auch nicht abmelden. "
                                      "Wenn du das <b>Daily Special</b> abonnieren möchtest, benutze den Command <b>/abo.</b> " + winking,
                                 parse_mode="HTML")

# Job Queue erstellen (ist an Updater gebunden!)
j = updater.job_queue

def send_ds(context):
    for i in abolist:
        context.bot.send_message(chat_id=i, text=daily_special(), parse_mode="HTML")


# run job queue, muss noch verändert werden, für Testzwecke alle 3600 sek, 1h
job_minute = j.run_repeating(send_ds, interval=36000, first=0)

#job_ds = j.run_daily(send_ds)

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply(update.message.text), parse_mode="HTML")

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

abo_stophandler = CommandHandler("abo_stop", abo_stop)
dispatcher.add_handler(abo_stophandler)

echohandler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echohandler)

# muss als letztes zum dispatcher hinzugefügt werden
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
