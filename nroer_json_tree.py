import urllib
import json
import requests
import ast
import re
from constants import kinds

class nroer_json_tree():
	
	def open_csv(self):
		"""This function is used to open files.csv file to fetch URLs"""
		with open('created_at.json') as f:
			self.data = json.load(f)
	
		
	def nroer_channel(self):
		"""This function used to create channel json fwith NROER JSON Channel tree structure. """
		nroer_json_tree =  dict(description = 'This channel was created from the files in the contentdirectory and the metadata in nroer_json_tree.json',
			language = 'en',
			source_domain = 'nroer.gov.in',
			source_id = 'nroer-json-channel_25',
			thumbnail = 'https://nroer.gov.in/static/ndf/css/themes/nroer/logo.png',
			title = 'NROER JSON channel',
			children = [],
			)
		nroer_theme = dict(
				kind = kinds.TOPIC,
				title='Theme',
				source_id='theme_topic',
				description='This directory will contain all the data with the nodes which are included in theme tree of NROER',
				language='en',
				thumbnail='https://nroer.gov.in/static/ndf/css/themes/nroer/images/default-bg.png',
				license= kinds.LICENSE,
				children=[],
				)
		nroer_json_tree['children'].append(nroer_theme)
		self.nroer_level_1_item(nroer_theme)
		with open('nroer_json_tree_2.json', 'w') as fp:
				json.dump(nroer_json_tree, fp,indent=2)
				fp.write("\n")
				
	def nroer_level_1_item(self,nroer_theme):
		"""This function will build the hierarchy of nroer_level_1_item topic and appending to children attribute of 'nroer_json_tree'(dict) """
		chef.open_csv()
		data_source_id = []
		nroer_topic_item_orphan = []
		for key in self.data:
			file_url = 'https://nroer.gov.in/api/v1?created_at='+ key
			url_obj = urllib.request.urlopen(file_url)
			result = url_obj.read().decode('utf-8')
			nroer_data_json = json.loads(result)	
			member_of =  nroer_data_json[0]['member_of'][0]
			type =  nroer_data_json[0]['if_file']['mime_type']
			prior_node = nroer_data_json[0]['prior_node']
			title = nroer_data_json[0]['name']
			source_id = nroer_data_json[0]['_id']
			description = nroer_data_json[0]['content']
			language = nroer_data_json[0]['language'][0]
			Copyright = nroer_data_json[0]['created_by']
			thumbnail = nroer_data_json[0]['if_file']['thumbnail']['relurl']
			if (member_of =="theme_item" or member_of == "Topic"):
				nroer_topic_item_dict = dict(
				kind=kinds.TOPIC,
				title=title,
				source_id=source_id,
				description=description,
				language=language,
				thumbnail=thumbnail,
				license=kinds.LICENSE,
				children=[],
				)
				#nroer_topic_item_dict = self.process_topic_orphan(nroer_topic_item_orphan,nroer_topic_item_dict)
				if (prior_node == ['National Curriculum'] ):
					nroer_theme['children'].append(nroer_topic_item_dict)
				else:
					source_ids = nroer_topic_item_dict.get('source_id')
					data_source_id.append(source_ids)
					nroer_theme = self.fetch_parent_id(nroer_theme,data_source_id)
					nroer_theme = self.match_source_id_and_store_as_child(nroer_theme, nroer_topic_item_dict)
			
		
	def fetch_parent_id(self,nroer_theme,data_source_id):
		for element in data_source_id:
			url = 'https://nroer.gov.in/dev/query/'+ element
			page = requests.get(url).content
			page1 = page.decode('utf-8')
			pattern = re.compile('= (.*?);')
			matches = pattern.search(page1)
			matched = matches.group(1)
			d= matched
			data = ast.literal_eval(d)
			dict={}
			for i in data:
				dict[i[0]] = i[1:]
		string_a = i.replace("'","")
		d = json.loads(string_a)
		x = d.get('prior_node')
		print(x)
		
	def match_source_id_and_store_as_child(self,nroer_theme, nroer_topic_item_dict):
		for element in nroer_theme['children']['children']:
			print(element)
			
	#def process_topic_orphan(nroer_topic_item_orphan,nroer_topic_item_dict):
		
		
if __name__ == '__main__':
	chef = nroer_json_tree()
	chef.open_csv()
	chef.nroer_channel()