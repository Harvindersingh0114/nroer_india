import urllib
import json
import requests
"""Request to connect to the URL"""
with open('created_at.json') as f:
	data = json.load(f)
for key in data:	
	url ='https://nroer.gov.in/api/v1?created_at=' + key
	obj = urllib.request.urlopen(url)
	str_res = obj.read().decode('utf-8')
	djson = json.loads(str_res)
	print(type(djson))
	"""Mapping values from the API"""
	Path = djson[0]['if_file']['original']['relurl']
	Title = djson[0]['name']
	Source_ID = djson[0]['_id']
	Description = djson[0]['content']
	Author = djson[0]['source']
	Language = djson[0]['language'][0]
	Copyright = djson[0]['created_by']
	Thumbnail = djson[0]['if_file']['thumbnail']['relurl']
	#print('Path:%s\nTitle:%s\nSource_ID:%s\nDescription:%s\nAuthor:%s\nLanguage:%s\nCopyright:%s\nThumbnail :%s'%(Path,Title,Source_ID,Description,Author,Language,Copyright,Thumbnail))
	"""Store Values into JSON File"""


	"""Dictionary to store data into JSON File"""
	my_dict = {'Path':Path,
	'Title':Title,
	'Source_ID':Source_ID,
	'Description':Description,
	'Author':Author,
	'Language':Language,
	'Copyright':Copyright,
	'Thumbnail':Thumbnail,
	}
	print(my_dict)
def pp_json(json_thing, sort=True, indents=4):
	if type(json_thing) is str:
		print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
	else:
		print(json.dumps(json_thing, sort_keys=sort, indent=indents))
	return None
pp_json(my_dict)

