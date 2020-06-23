# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/3.7"
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    print(sparql.query().convert())
    return sparql.query().convert()


def get_general_facts(endpoint_url, person):
    query = """SELECT ?birthdate ?birthplaceLabel ?deathdate ?deathplaceLabel ?deathcauseLabel ?fatherLabel ?motherLabel ?spouseLabel
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
  SERVICE wikibase:label {{bd:serviceParam wikibase:language "en" }}
}}

""".format(person=person)
    return(get_results(endpoint_url, query))

get_general_facts(endpoint_url, "Q2893991")
