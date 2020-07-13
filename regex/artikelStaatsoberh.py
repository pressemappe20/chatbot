import re

text_to_search_1 ='''
Nenn mir Artikel zu Staatsoberhäuptern von Deutschland.
Gib mir Artikel zu Staatsoberhäuptern von Dänemark.
Ich brauche Artikel über Staatsoberhäupter von Frankreich.
'''

pattern = re.compile(r'(\w+\s\w+)\s(Artikel)\s(\w+)\s(Staatsoberhäuptern|Staatsoberhäupter)\s(\w+)\s(\w+)')

matches = pattern.finditer(text_to_search_1)


for match in matches:
    print(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6))