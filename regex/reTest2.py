import re

text_to_search_1 ='''
Wie heißen die Kinder von Queen Elizabeth?
Wie heißen die Kinder von Stalin?
Wie heißen die Kinder von Roosevelt?
'''

pattern = re.compile(r'(Wi?e?)\s(heißen)\s(die)\s(Kinder)\s(von)\s((\w+)\s?(\w+)?)')

matches = pattern.finditer(text_to_search_1)


for match in matches:
    print(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6))