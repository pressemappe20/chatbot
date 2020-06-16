# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/3.7" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    print(sparql.query().convert())
    return sparql.query().convert()


def get_lengthpositionheld(endpoint_url, person):
    query = """
SELECT ?position ?positionLabel ?starttime ?endtime ?length
WHERE 
{{
  wd:{person} p:P39 [
    ps:P39 ?position ;
    pq:P580 ?starttime ;
    pq:P582 ?endtime 
            ] .
  BIND(?endtime - ?starttime AS ?lengthInDays).
  BIND(?lengthInDays/365.2425 AS ?lengthInYears).
  BIND(FLOOR(?lengthInYears) AS ?length).
  service wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE], en, de, fr, es, nl, pl, ru" . }}
  }}

""".format(person=person)
    return(get_results(endpoint_url, query))

get_lengthpositionheld(endpoint_url, "Q230238")
