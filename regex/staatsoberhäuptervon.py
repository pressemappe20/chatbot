import re

text_to_search_1 ='''
Nenne mir weibliche Staatsoberhäupter von Deutschland.
Nenne mir Artikel zu weiblichen Staatsoberhäuptern von Deutschland.
Ich suche weibliche Staatsoberhäupter von England. 
Ich suche männliche Staatsoberhäupter von Schweden. 

'''

pattern = re.compile(r'(\w+\s?\w+\s?\w+?\s?\w+?)\s(männliche|weibliche)\s(Staatsoberhäupter|Staatsoberhäuptern)\s(von)\s(\w+)')

matches = pattern.finditer(text_to_search_1)


for match in matches:
    print(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5))