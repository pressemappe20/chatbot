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


def get_childcount(endpoint_url, person):
    query =  """SELECT (COUNT(?child) AS ?count)
WHERE
{{
  wd:{person} wdt:P40 ?child .
}}

""".format(person=person)
    return(get_results(endpoint_url, query))


get_childcount(endpoint_url,"Q1339")
