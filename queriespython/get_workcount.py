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


def get_workcount(endpoint_url, count):
    query = """PREFIX schema: <http://schema.org/>
PREFIX zbwext: <http://zbw.eu/namespaces/zbw-extensions/>
#
select distinct ?item ?itemLabel ?pm20 ?viewer ?workCount
where {
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
  filter(?workCount > {count})
  # viewer link
  bind(substr(?pm20Id, 4, 4) as ?numStub)
  bind(substr(?pm20Id, 4, 6) as ?num)
  bind(uri(concat('http://dfg-viewer.de/show/?tx_dlf[id]=http://zbw.eu/beta/pm20mets/', ?numStub, 'xx/', ?num, '.xml')) as ?viewer)
  # add labels
  service wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE], en, de, fr, es, nl, pl, ru" . }}
}}
order by ?itemLabel
""".format(count=count)
    return (get_results(endpoint_url, query))


get_workcount(endpoint_url, "100")
