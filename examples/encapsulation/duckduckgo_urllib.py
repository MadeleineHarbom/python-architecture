import json
from urllib.request import urlopen
from urllib.parse import urlencode
import pprint

printer = pprint.PrettyPrinter()

params = dict(q='Sausages', format='json')
url = 'http://api.duckduckgo.com' + '?' + urlencode(params)
handle = urlopen(url)
raw_text = handle.read().decode('utf8')
parsed = json.loads(raw_text)
printer.pprint(parsed)


results = parsed['RelatedTopics']
for r in results:
    if 'Text' in r:
        print(r['FirstURL'] + ' - ' + r['Text'])