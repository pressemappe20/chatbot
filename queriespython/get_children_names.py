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


def get_names_children(endpoint_url, person):
    query = """SELECT ?child ?childLabel 
WHERE
{{
  wd:{person} wdt:P40 ?child .
SERVICE wikibase:label {{bd:serviceParam wikibase:language "en" }}
}}


""".format(person=person)
    return(get_results(endpoint_url, query))

get_names_children(endpoint_url, "Q230238")
