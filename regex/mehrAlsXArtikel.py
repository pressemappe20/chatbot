import re

text_to_search ='''
Welche Staatsoberhäupter haben mehr als 5 Artikel in der Pressemappe? 
Zu welchen Staatsoberhäuptern gibt es mehr als 7 Artikel in der PM20?
Zeig mir Staatsoberhäupter mit mehr als 3 Artikeln in der Pressemappe
'''

pattern = re.compile(r'(\w+\s?\w+?)\s(Staatsoberhäupter|Staatsoberhäuptern)\s(\w+\s\w+\s\w+\s?\w+?)\s(\d)\s(Artikel|Artikeln)\s(\w+\s\w+)\s(Pressemappe|PM20)')

matches = pattern.finditer(text_to_search)

for match in matches:
    print(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6), match.group(7))