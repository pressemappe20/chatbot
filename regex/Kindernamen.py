import re

text_to_search_1 ='''
Wie heißen die Kinder von Queen Elizabeth?
Wie heißen die Kinder von Josef Stalin?
Wie heissen die Kinder von Roosevelt?
Wer sind die Kinder von Stalin?
'''

pattern = re.compile(r'(\w+)\s(heißen|heissen|sind)\s(\w+)\s(Kinder)\s(\w+)\s((\w+)\s?(\w+)?)')

matches = pattern.finditer(text_to_search_1)


for match in matches:
    print(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6))