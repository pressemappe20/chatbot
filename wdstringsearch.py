# Hier finden sich sämtliche Funktionen, die die qids von erkannten strings erleichtern sollen. Diese qids können im
# Anschluss Teil der tatsächlichen Recherche in wikidata werden.

# Eventuell muss hier ein dictionary eingebaut werden, das widerspiegelt, welche Daten gesucht werden können
# In diesem dictionary können beispielsweise auch die Zeilen eingespeichert sein, die den Unterschied beim Abfragen
# machen.

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT distinct ?item ?itemLabel ?itemDescription WHERE{  
  ?item ?label "%s"@de.  
  ?item wdt:P31 wd:Q6256 .
  ?article schema:about ?item .
  ?article schema:inLanguage "en" .
  ?article schema:isPartOf <https://en.wikipedia.org/>.	
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
}"""


def start():
    while True:
        searchobject = input("Nach welchem Land soll ich für dich suchen? ")
        try:
            print(get_country(endpoint_url, query, searchobject))
        except IndexError:
            print("Fehler")


def get_country(endpoint_url, query, name):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    fullquery = query % name
    sparql.setQuery(fullquery)
    sparql.setReturnFormat(JSON)
    searchresults = sparql.query().convert()
    return searchresults["results"]["bindings"][0]["item"]["value"].replace("http://www.wikidata.org/entity/", "")


start()
