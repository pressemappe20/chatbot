# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import json
import random
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    #print(sparql.query().convert())
    return sparql.query().convert()

def get_random_staatsoberhaupt (endpoint_url):
    query = """PREFIX schema: <http://schema.org/>
    PREFIX zbwext: <http://zbw.eu/namespaces/zbw-extensions/>
    SELECT DISTINCT ?item ?itemLabel ?pm20 ?viewer ?workCount ?birthdate ?birthplaceLabel ?deathdate ?deathplaceLabel ?deathcauseLabel ?fatherLabel ?motherLabel ?spouseLabel ?pic
    where {
  # get the basic set of persons with "field of activity"
  # "Staatsoberhaupt" from PM20 endpoint
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
         OPTIONAL {?item wdt:P18 ?pic . }
  #
  # restrict to items with online accessible articles
    ?item p:P4293/pq:P5592 ?workCount .
    filter(?workCount > 0)
  # viewer link
    bind(substr(?pm20Id, 4, 4) as ?numStub)
    bind(substr(?pm20Id, 4, 6) as ?num)
    bind(uri(concat('http://dfg-viewer.de/show/?tx_dlf[id]=http://zbw.eu/beta/pm20mets/pe/', ?numStub, 'xx/', ?num, '.xml')) as ?viewer)
  # add labels
    service wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE], en, de, fr, es, nl, pl, ru" . }
    }
        """
    return (get_results(endpoint_url, query))


#ergebnisse in variable speichern
resultjson = get_random_staatsoberhaupt(endpoint_url)


def daily_special():
    #funktion returned namen des staatsoberhaupts und nichts anderes.............
    def daily_staatsoberhaupt():
        name = resultjson['results']['bindings'][0]['itemLabel']['value']
        return name
    daily_staatsoberhaupt()

    def daily_birthdate():
        birthdate = resultjson['results']['bindings'][0]['birthdate']['value']
        return birthdate
    daily_birthdate()

    #returned namen des orts und nichts anderes......
    def daily_birthplace():
        try:
            birthplace = resultjson['results']['bindings'][0]['birthplaceLabel']['value']
            if birthplace.startswith('Q') == True:
                return None
            else:
                return birthplace
        except KeyError:
            return None
    daily_birthdate()

    def daily_deathdate():
        try:
            deathdate = resultjson['results']['bindings'][0]['deathdate']['value']
            return deathdate
        except KeyError:
            return None
    daily_deathdate()

    def daily_deathplace():
        try:
            deathplace = resultjson['results']['bindings'][0]['deathplaceLabel']['value']
            if deathplace.startswith('Q') == True:
                return None
            else:
                return deathplace
        except KeyError:
            return None
    daily_deathplace()

    def daily_mother():
        try:
            mother = resultjson['results']['bindings'][0]['motherLabel']['value']
            if mother.startswith('Q') == True:
                return None
            else:
                return mother
        except KeyError:
            return None
    daily_mother()

    def daily_father():
        try:
            father = resultjson['results']['bindings'][0]['fatherLabel']['value']
            if father.startswith('Q') == True:
                return None
            else:
                return father
        except KeyError:
            return None
    daily_father()

    def daily_spouse():
        try:
            spouse = resultjson['results']['bindings'][0]['spouseLabel']['value']
            if spouse.startswith('Q') == True:
                return None
            else:
                return spouse
        except KeyError:
            return None
    daily_spouse()

    print("Staatsoberhaupt des Tages:", daily_staatsoberhaupt())
    print("Geburtsdatum: ", daily_birthdate())
    print("Geburtsort:", daily_birthplace())
    print("Sterbedatum:", daily_deathdate())
    print("Sterbeort: ",daily_deathplace())
    print("Mutter: ", daily_mother())
    print("Vater: ", daily_mother())
    print("Ehepartner: ", daily_spouse())

daily_special()

