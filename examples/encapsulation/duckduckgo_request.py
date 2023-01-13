import requests
import pprint

printer = pprint.PrettyPrinter()

params = dict(q='Sausages', format='json')
parsed = requests.get('http://api.duckduckgo.com', params=params).json()
printer.pprint(parsed)

results = parsed['RelatedTopics']
printer.pprint(results)
for r in results:
    if 'Text' in r:
        print(r['FirstURL'] + ' - ' + r['Text'])
