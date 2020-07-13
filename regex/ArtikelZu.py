import re

text_to_search ='''
Ich suche Artikel zu Josef Stalin.
Ich brauche Artikel zu Queen Elizabeth. 
Gib mir Artikel über Hitler.  
'''

pattern = re.compile(r'(\w+\s?\w+?)\s(Artikel)\s(\w+)\s((\w+)\s?(\w+))')

matches = pattern.finditer(text_to_search)

for match in matches:
    print(match.group(4))
