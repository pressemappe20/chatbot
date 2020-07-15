# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import random
import time
from datetime import datetime
import schedule
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"


def get_results(endpoint_url, query):
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
    return (get_results(endpoint_url, query))


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

    print("Staatsoberhaupt des Tages:", daily_staatsoberhaupt())
    print("Beschreibung:", daily_description())
    print("Geburtsdatum: ", daily_birthdate())
    print("Geburtsort:", daily_birthplace())
    print("Sterbedatum:", daily_deathdate())
    print("Sterbeort: ", daily_deathplace())
    print("Mutter: ", daily_mother())
    print("Vater: ", daily_mother())
    print("Ehepartner: ", daily_spouse())
    print("Bild: ", daily_pic())
    print("--------------------------------------")


schedule.every(1).minutes.do(daily_special)

while True:
    schedule.run_pending()
    time.sleep(1)
