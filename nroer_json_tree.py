import urllib
import json
import requests
import ast
import re
from constants import kinds

class nroer_json_tree():
	
	def open_file(self):
		"""This function is used to open created_at.json file to fetch URLs"""
		with open('created_at.json') as f:
			self.data = json.load(f)

	def nroer_channel(self):
		"""This function used to create channel json fwith NROER-INDIA Channel tree structure. """
		topic_item_orphan = []
		nroer_json_tree =  dict(description = 'This channel was created from the files in the contentdirectory and the metadata in nroer_json_tree.json',
			language = 'en',
			source_domain = 'nroer.gov.in',
			source_id = 'nroer-json-channel_25',
			thumbnail = 'https://nroer.gov.in/static/ndf/css/themes/nroer/logo.png',
			title = 'NROER-INDIA',
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
		self.nroer_level_1_item(nroer_theme,topic_item_orphan)
		with open('nroer_json_tree.json', 'w') as fp:
				json.dump(nroer_json_tree, fp,indent=2)
				fp.write("\n")
				
	def nroer_level_1_item(self,nroer_theme,topic_item_orphan):
		"""This function will build the hierarchy of nroer_level_1_item topic and appending to children attribute of 'nroer_json_tree'(dict) """
		chef.open_file()
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
			copyright = nroer_data_json[0]['created_by']
			thumbnail = nroer_data_json[0]['if_file']['thumbnail']['relurl']
			path = nroer_data_json[0]['if_file']['original']['relurl']
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
		
				if (prior_node == ['National Curriculum'] ):
					nroer_theme = self.append_child(nroer_theme,nroer_topic_item_dict)
				else:
					nroer_topic_item_dict = self.fetch_parent_id(nroer_topic_item_dict)
					nroer_topic_item_dict = self.match_source_id_and_store_as_child(nroer_theme, nroer_topic_item_dict)

			elif (member_of == "File") :
				if (type=="application/pdf"):
					nroer_file_item_dict = dict (
					kind = kinds.DOCUMENT,
					title = title,
					description = description,
					source_id = source_id,
					language = language,
					thumbnail = thumbnail,
					files = [ ],
					license = dict(license_id = kinds.LICENSE,
						description = "",
						copyright_holder = copyright)
					)
					
					file_dict = dict(file_type = kinds.DOCUMENT,
						path = 'https://nroer.gov.in/media/'+path,
						language = language)
					nroer_file_item_dict['files'].append(file_dict)						
					nroer_file_item_dict = self.fetch_file_parent_id(nroer_file_item_dict)
					nroer_file_item_dict = self.find_prior_node_in_theme_topics(nroer_theme,nroer_file_item_dict)
				

	def match_source_id_and_store_as_child(self,nroer_theme, nroer_topic_item_dict):
		for nroer_child in nroer_theme['children']:
			if nroer_child['source_id'] in nroer_topic_item_dict['prior_node'] :
				nroer_child = self.append_child(nroer_child,nroer_topic_item_dict)
				if (nroer_topic_item_dict['kind'] == 'topic'):
					return nroer_theme
			else:
				self.match_source_id_and_store_nroer_child_as_child(nroer_child, nroer_topic_item_dict)
		return nroer_theme

	def match_source_id_and_store_nroer_child_as_child(self,nroer_child, nroer_topic_item_dict):
		for child in nroer_child['children']:
			if child['source_id'] in nroer_topic_item_dict['prior_node']:
				child = self.append_child(child,nroer_topic_item_dict)
				
				
	def fetch_parent_id(self,nroer_topic_item_dict):
		data_source_id = []
		source_ids = nroer_topic_item_dict.get('source_id')
		data_source_id.append(source_ids)
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
		prior_node = d.get('prior_node')
		prior_node = "".join(prior_node)
		nroer_topic_item_dict['prior_node'] = prior_node
		return nroer_topic_item_dict

	"""File Processing"""	
	def fetch_file_parent_id(self,nroer_file_item_dict):
		file_source_id = []
		source_ids = nroer_file_item_dict.get('source_id')
		file_source_id.append(source_ids)
		for id in file_source_id:
			url = 'https://nroer.gov.in/dev/query/' + id
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
				dict[i[1]] = i[1:]
			
		string_a = i.replace("'","")
		d = json.loads(string_a)
		file_prior_node_id = d.get('relation_set')[0]['teaches']
		nroer_file_item_dict['prior_node'] = file_prior_node_id
		return nroer_file_item_dict

	def find_prior_node_in_theme_topics(self,nroer_theme,nroer_file_item_dict):
		for theme_item in nroer_theme['children']:
			if theme_item['source_id'] in nroer_file_item_dict['prior_node']:
				theme_item = self.append_child(nroer_theme,nroer_file_item_dict)
			else:
				self.find_prior_node_in_theme_item_topics(theme_item,nroer_file_item_dict)
		return nroer_theme
		
	def find_prior_node_in_theme_item_topics(self,theme_item,nroer_file_item_dict):
		for topic_item in theme_item['children']:
			if topic_item['source_id'] in nroer_file_item_dict['prior_node']:
				topic_item = self.append_child(topic_item,nroer_file_item_dict)
			else:
				self.find_prior_node_in_topics(topic_item,nroer_file_item_dict)
		
	def find_prior_node_in_topics(self,topic_item,nroer_file_item_dict):
		for topic in topic_item['children']:
			if topic['source_id'] in nroer_file_item_dict['prior_node']:
				topic = self.append_child(topic,nroer_file_item_dict)
				
	def append_child(self,nroer_theme,nroer_topic_item_dict):
		nroer_theme['children'].append(nroer_topic_item_dict)
		return nroer_theme
	
if __name__ == '__main__':
	chef = nroer_json_tree()
	chef.open_file()
	chef.nroer_channel()