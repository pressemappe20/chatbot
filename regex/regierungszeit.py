import re

text_to_search ='''
Wie lang hat Stalin regiert?
Wie lange hat Josef Stalin regiert?
Wie lange hat Queen Elizabeth regiert?
'''

pattern = re.compile(r'(\w+)\s(\w+)\s(\w+)\s(\w+\s?\w+?)\s(regiert)')

matches = pattern.finditer(text_to_search)

for match in matches:
    print(match.group(4))
