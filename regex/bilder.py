import re

text_to_search_1 ='''
Zeig mir Bilder von Stalin.
Ich suche Bilder von Josef Stalin.
Gib mir Bilder zu Josef Stalin. 
'''

pattern = re.compile(r'(\w+)\s(\w+)\s(Bilder)\s(\w+)\s((\w+)\s?(\w+))')

matches = pattern.finditer(text_to_search_1)

for match in matches:
    print(match.group(5))
