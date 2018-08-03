import urllib
import json
import requests
import ast
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
from le_utils.constants import content_kinds, file_types, exercises, licenses
from ricecooker.chefs import JsonTreeChef
from ricecooker.classes.licenses import get_license
from ricecooker.utils.jsontrees import write_tree_to_json_tree

class NroerChannelJsonChef(JsonTreeChef):
	
	def pre_run(self,args,options):
		"""Function to generate nroer_channel_tree and will write tree into json tree"""
		nroer_channel_tree =  dict(
			description = 'This channel was created from the files in the contentdirectory and the metadata in nroer_json_tree.json',
			language = 'en',
			source_domain = 'nroer.gov.in',
			source_id = 'nroer-json-channel_25_6',
			thumbnail = 'https://nroer.gov.in/static/ndf/css/themes/nroer/logo.png',
			title = 'NROER-INDIA',
			children = [],
			)		
		self.create_theme_nodes(nroer_channel_tree)
		
		json_tree_path = self.get_json_tree_path()
		write_tree_to_json_tree(json_tree_path, nroer_channel_tree)
		
	def create_theme_nodes(self,nroer_channel_tree):
		"""Function to generate and append nroer_theme_tree in to channel tree"""
		nroer_theme_tree = dict(
			kind = content_kinds.TOPIC,
			title='Theme',
			source_id='theme_topic',
			description='This directory will contain all the data with the nodes which are included in theme tree of NROER',
			language='en',
			thumbnail='https://nroer.gov.in/static/ndf/css/themes/nroer/images/default-bg.png',
			license= licenses.CC_BY_SA,
			children=[],
			)
		nroer_channel_tree['children'].append(nroer_theme_tree)
		self.node_attributes(nroer_theme_tree)
		
	def open_file(self):
		"""This function is used to open created_at.json file to fetch URLs"""
		with open('created_at.json') as f:
			self.created_at = json.load(f)
	def node_attributes(self,nroer_theme_tree):
		chef.open_file()
		for dates in self.created_at:
			self.node_url = 'https://nroer.gov.in/api/v1?created_at='+ dates
			url_obj = urllib.request.urlopen(self.node_url)
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
				self.nroer_theme_item(nroer_theme_tree)
			elif(self.member_of == "File"):
				self.nroer_content_node(nroer_theme_tree)

	def nroer_theme_item(self,nroer_theme_tree):
		nroer_topic_node = dict(
			kind=content_kinds.TOPIC,
			title=self.title,
			source_id=self.source_id,
			description=self.description,
			language=self.language,
			thumbnail= self.thumbnail,
			license=licenses.CC_BY_SA,
			children=[],
			)
			
		if (self.member_of == "Topic"):
			html_link = urlopen(self.node_url)
			soups = BeautifulSoup(html_link, 'html.parser')
			p_tag = soups.find('p')
			topic_node_description = p_tag.text.strip('\\n')
			nroer_topic_node['description'] = topic_node_description

		if (self.prior_node == ['National Curriculum'] ):
			nroer_theme_tree = self.append_child(nroer_theme_tree,nroer_topic_node)
		else:
			nroer_topic_node = self.extract_json_from_html(nroer_topic_node)
			nroer_topic_node = self.match_source_id_and_store_as_child(nroer_theme_tree, nroer_topic_node)

	def extract_json_from_html(self,nroer_topic_node):
		"""Function to fetch prior_node_id as prior_node from dev/query and append in to item dictionary."""
		node_html = 'https://nroer.gov.in/dev/query/'+ nroer_topic_node['source_id']
		node_html_content = requests.get(node_html).content
		html_data = node_html_content.decode('utf-8')
		node_reg_expression = re.compile('= (.*)\\n*;')
		search_html = node_reg_expression.search(html_data)
		node_data = search_html.group(1)
		node_json_value = ast.literal_eval(node_data)
		node={}
		for __string__ in node_json_value:
			node[__string__[0]] = __string__[1:]
		string_replace = __string__.replace("'","")
		node_item = json.loads(string_replace)
		if (nroer_topic_node['kind'] == "topic"):
			nroer_topic_node['prior_node_id'] = node_item['prior_node']
		else:
			nroer_topic_node['prior_node_id'] = node_item['relation_set'][0]['teaches']
		return nroer_topic_node
		
	def match_source_id_and_store_as_child(self,nroer_theme_tree, nroer_topic_node):
		"""This function will compare theme source_id and append topic to the nroer_theme tree."""
		for nroer_child in nroer_theme_tree['children']:
			if nroer_child['source_id'] in nroer_topic_node['prior_node_id'] :
				nroer_child = self.append_child(nroer_child,nroer_topic_node)
				nroer_topic_node.pop('prior_node_id')
				if (nroer_topic_node['kind'] == 'topic'):
					return nroer_theme_tree
			else:
				self.match_source_id_and_store_as_child(nroer_child, nroer_topic_node)
		return nroer_theme_tree
		
	def nroer_content_node(self,nroer_theme_tree):
		file_node = urlopen(self.node_url)
		soups = BeautifulSoup(file_node, 'html.parser')
		p_tag = soups.find('p')
		file_description = p_tag.text.strip('\\n')
		nroer_content_node = dict (
			title = self.title,
			description = file_description,
			source_id = self.source_id,
			language = self.language,
			thumbnail = self.thumbnail,
			files = [ ],
			license = dict(license_id = licenses.CC_BY_SA,
				description = "",
				copyright_holder = self.copyright)
			)
			
		file_dict = dict(
			path = 'https://nroer.gov.in/media/'+ self.path,
			language = self.language)
		nroer_content_node['files'].append(file_dict)	
		if (self.type=="application/pdf"):
			nroer_content_node.update(kind = content_kinds.DOCUMENT)
			file_dict.update(file_type = content_kinds.DOCUMENT)
		elif (self.type=="video/mp4"):
			nroer_content_node.update(kind = content_kinds.VIDEO,
			thumbnail = 'https://nroer.gov.in/media/' + self.thumbnail)
			file_dict.update(file_type = content_kinds.VIDEO)
		elif (self.type=="audio/mpeg"):
			nroer_content_node.update(kind = content_kinds.AUDIO)
			file_dict.update(file_type = content_kinds.AUDIO)
		else:
			print('kind not supported')
		nroer_content_node = self.extract_json_from_html(nroer_content_node)
		nroer_content_node = self.find_prior_node_in_theme_topics(nroer_theme_tree,nroer_content_node)
		
	def find_prior_node_in_theme_topics(self,nroer_theme_tree,nroer_content_node):
		for theme_item in nroer_theme_tree['children']:
			for topic_item in theme_item['children']:
				for topic in topic_item['children']:
					if topic['source_id'] in nroer_content_node['prior_node_id']:
						topic = self.append_child(topic,nroer_content_node)
		return nroer_theme_tree
	
	def append_child(self,nroer_theme_tree,nroer_topic_node):
		"""Function to append all kind of nodes into tree"""
		nroer_theme_tree['children'].append(nroer_topic_node)
		return nroer_theme_tree
		
if __name__ == '__main__':
    chef = NroerChannelJsonChef()
    chef.main()