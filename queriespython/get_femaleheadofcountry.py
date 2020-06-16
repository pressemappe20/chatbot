# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    print(sparql.query().convert())
    return sparql.query().convert()


def get_femaleheadofcountry(endpoint_url, country):
    query = """PREFIX schema: <http://schema.org/>
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
  bind(uri(concat('http://dfg-viewer.de/show/?tx_dlf[id]=http://zbw.eu/beta/pm20mets/', ?numStub, 'xx/', ?num, '.xml')) as ?viewer)
  service wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE], en, de, fr, es, nl, pl, ru" . }}
  ?item wdt:P21 wd:Q6581072 .
  ?item wdt:P27 wd:{country}.
  }}



""".format(country=country)
    return (get_results(endpoint_url, query))


get_femaleheadofcountry(endpoint_url, "Q34")