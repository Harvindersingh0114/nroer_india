import urllib
import json
import requests
import ast
import re
from constants import kinds

class nroer_channel:
	def __init__(self):
		"""Function to generate channel dictionary"""
		self.nroer_json_tree =  dict(description = 'This channel was created from the files in the contentdirectory and the metadata in nroer_json_tree.json',
			language = 'en',
			source_domain = 'nroer.gov.in',
			source_id = 'nroer-json-channel_25',
			thumbnail = 'https://nroer.gov.in/static/ndf/css/themes/nroer/logo.png',
			title = 'NROER-INDIA',
			children = [],
			)		

class nroer_theme(nroer_channel):		
	def create_theme_dictionary(self):
		"""Function to generate and append nroer_theme_tree in to channel tree"""
		self.nroer_theme = dict(
				kind = kinds.TOPIC,
				title='Theme',
				source_id='theme_topic',
				description='This directory will contain all the data with the nodes which are included in theme tree of NROER',
				language='en',
				thumbnail='https://nroer.gov.in/static/ndf/css/themes/nroer/images/default-bg.png',
				license= kinds.LICENSE,
				children=[],
				)
		self.nroer_json_tree['children'].append(self.nroer_theme)
		

class theme_item_topic(nroer_theme):
	def open_file(self):
		"""This function is used to open created_at.json file to fetch URLs"""
		with open('created_at.json') as f:
			self.data = json.load(f)

	def nroer_level_1_item(self):
		"""This function will build the hierarchy of nroer_level_1_item topic and appending to children attribute of 'nroer_json_tree'(dict) """
		theme.open_file()
		for key in self.data:
			file_url = 'https://nroer.gov.in/api/v1?created_at='+ key
			url_obj = urllib.request.urlopen(file_url)
			result = url_obj.read().decode('utf-8')
			nroer_data_json = json.loads(result)	
			self.member_of =  nroer_data_json[0]['member_of'][0]
			self.type =  nroer_data_json[0]['if_file']['mime_type']
			self.prior_node = nroer_data_json[0]['prior_node']
			self.title = nroer_data_json[0]['name']
			self.source_id = nroer_data_json[0]['_id']
			self.description = nroer_data_json[0]['content']
			self.language = nroer_data_json[0]['language'][0]
			self.copyright = nroer_data_json[0]['created_by']
			self.thumbnail = nroer_data_json[0]['if_file']['thumbnail']['relurl']
			self.path = nroer_data_json[0]['if_file']['original']['relurl']
			
			if (self.member_of =="theme_item" or self.member_of == "Topic"):
				nroer_topic_item_dict = dict(
				kind=kinds.TOPIC,
				title=self.title,
				source_id=self.source_id,
				description=self.description,
				language=self.language,
				thumbnail= self.thumbnail,
				license=kinds.LICENSE,
				children=[],
				)
		
				if (self.prior_node == ['National Curriculum'] ):
					self.nroer_theme = self.append_child(self.nroer_theme,nroer_topic_item_dict)
				else:
					nroer_topic_item_dict = self.fetch_parent_id(nroer_topic_item_dict)
					nroer_topic_item_dict = self.match_source_id_and_store_as_child(self.nroer_theme, nroer_topic_item_dict)

			elif (self.member_of == "File") :
				if (self.type=="application/pdf"):
					self.document_kind(self.nroer_level_1_item)
				elif (self.type=="video/mp4"):
					self.video_kind(self.nroer_level_1_item)
						
					
	def document_kind(self,nroer_level_1_item):
		"""Function to create dictionary for kind as document."""
		nroer_file_item_dict = dict (
		kind = kinds.DOCUMENT,
		title = self.title,
		description = self.description,
		source_id = self.source_id,
		language = self.language,
		thumbnail = self.thumbnail,
		files = [ ],
		license = dict(license_id = kinds.LICENSE,
			description = "",
			copyright_holder = self.copyright)
		)
					
		self.file_dict = dict(file_type = kinds.DOCUMENT,
			path = 'https://nroer.gov.in/media/'+ self.path,
			language = self.language)
		nroer_file_item_dict['files'].append(self.file_dict)	
		nroer_file_item_dict = self.fetch_file_parent_id(nroer_file_item_dict)
		nroer_file_item_dict = self.find_prior_node_in_theme_topics(self.nroer_theme,nroer_file_item_dict)
		
	def video_kind(self,nroer_level_1_item):
		"""Function to create dictionary for kind as video."""
		nroer_file_item_dict_video = dict (
		kind = kinds.VIDEO,
		title = self.title,
		description = self.description,
		source_id = self.source_id,
		language = self.language,
		thumbnail = self.thumbnail,
		files = [ ],
		license = dict(license_id = kinds.LICENSE,
			description = "",
			copyright_holder = self.copyright)
		)
					
		self.file_dict = dict(file_type = kinds.VIDEO,
			path = 'https://nroer.gov.in/media/'+ self.path,
			language = self.language)
		nroer_file_item_dict_video['files'].append(self.file_dict)	
		nroer_file_item_dict_video = self.fetch_file_parent_id(nroer_file_item_dict_video)
		nroer_file_item_dict_video = self.find_prior_node_in_theme_topics(self.nroer_theme,nroer_file_item_dict_video)		
	def fetch_parent_id(self,nroer_topic_item_dict):
		"""Function to fetch prior_node_id as prior_node from dev/query and append in to item dictionary."""
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
		
	def match_source_id_and_store_as_child(self,nroer_theme, nroer_topic_item_dict):
		"""This function will compare theme source_id and append topic to the nroer_theme tree."""
		for nroer_child in nroer_theme['children']:
			if nroer_child['source_id'] in nroer_topic_item_dict['prior_node'] :
				nroer_child = self.append_child(nroer_child,nroer_topic_item_dict)
				if (nroer_topic_item_dict['kind'] == 'topic'):
					return nroer_theme
			else:
				self.match_source_id_and_store_nroer_child_as_child(nroer_child, nroer_topic_item_dict)
		return nroer_theme

	def match_source_id_and_store_nroer_child_as_child(self,nroer_child, nroer_topic_item_dict):
		"""Function to compare values of second level of theme_items to append topics into nroer_theme tree."""
		for child in nroer_child['children']:
			if child['source_id'] in nroer_topic_item_dict['prior_node']:
				child = self.append_child(child,nroer_topic_item_dict)
				
	"""Following functions are defined to append file items into nroer_theme_tree with particular file relations."""
	
	def fetch_file_parent_id(self,nroer_file_item_dict):
		"""Function to fetch the realtons from 'teaches' key of file_item from dev/query and append into file_item_dict."""
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
		relation_set = d.get('relation_set')
		if (relation_set == []):
			print('No value')
		else:
			file_prior_node_id = d.get('relation_set')[0]['teaches']
			nroer_file_item_dict['prior_node'] = file_prior_node_id
		return nroer_file_item_dict
		
	def find_prior_node_in_theme_topics(self,nroer_theme,nroer_file_item_dict):
		"""Function to find respected topic source_id for file to append at nroer_theme_tree level."""
		for theme_item in nroer_theme['children']:
			if theme_item['source_id'] in nroer_file_item_dict['prior_node']:
				theme_item = self.append_child(nroer_theme,nroer_file_item_dict)
			else:
				self.find_prior_node_in_theme_item_topics(theme_item,nroer_file_item_dict)
		return nroer_theme
		
	def find_prior_node_in_theme_item_topics(self,theme_item,nroer_file_item_dict):
		"""Function to find respected topic source_id for file to append at theme_item level."""
		for topic_item in theme_item['children']:
			if topic_item['source_id'] in nroer_file_item_dict['prior_node']:
				topic_item = self.append_child(topic_item,nroer_file_item_dict)
			else:
				self.find_prior_node_in_topics(topic_item,nroer_file_item_dict)	
				
	def find_prior_node_in_topics(self,topic_item,nroer_file_item_dict):
		"""Function to find respected topic source_id for file to append at nroer_topic level."""
		for topic in topic_item['children']:
			if topic['source_id'] in nroer_file_item_dict['prior_node']:
				topic = self.append_child(topic,nroer_file_item_dict)
	
	
	def append_child(self,nroer_theme,nroer_topic_item_dict):
		"""Function to append all kind of nodes into tree"""
		nroer_theme['children'].append(nroer_topic_item_dict)
		with open('nroer_json_tree_class.json', 'w') as fp:
				json.dump(self.nroer_json_tree, fp,indent=2)
				fp.write("\n")
		return nroer_theme
		
if __name__ == '__main__':
	theme = theme_item_topic()
	theme.create_theme_dictionary()
	theme.nroer_level_1_item()