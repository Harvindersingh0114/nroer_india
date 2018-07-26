import re
import json
import requests
import ast

url = 'https://nroer.gov.in/dev/query/55b1f72181fccb7926fe5453'
page = requests.get(url).content
page1 = page.decode('utf-8')
pattern = re.compile('= (.*?);')
matches = pattern.search(page1)
matched = matches.group(1)
d= matched
data = ast.literal_eval(d)
#print(data)
dict={}
for i in data:
	dict[i[0]] = i[1:]
	
string_a = i.replace("'","")
d = json.loads(string_a)
x = d.get('prior_node')
print(x)
"""y = d['prior_node'][0]
print(y)"""