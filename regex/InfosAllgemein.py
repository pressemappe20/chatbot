import re

text_to_search ='''
Ich suche Informationen zu Josef Stalin.
Ich brauche allgemeine Informationen zu Queen Elizabeth. 
Gib mir Infos über Hitler.  
'''

pattern = re.compile(r'(\w+\s\w+\s?\w+?)\s(Informationen|Infos)\s(\w+)\s((\w+)\s?(\w+))')

matches = pattern.finditer(text_to_search)

for match in matches:
    print(match.group(1), match.group(2), match.group(3), match.group(4))