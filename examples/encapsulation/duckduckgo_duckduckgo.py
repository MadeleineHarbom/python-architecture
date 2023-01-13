#from duckduckgo_search import ddg
import duckduckgo3
import pprint

printer = pprint.PrettyPrinter()

restults = ddg('Sausages')
printer.pprint(restults)

for r in restults:
    print(r['href'])