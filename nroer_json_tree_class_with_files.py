import urllib
import json
import requests
import ast
import re
import logging
from bs4 import BeautifulSoup
from urllib.request import urlopen
from le_utils.constants import content_kinds, file_types, exercises, licenses
from ricecooker.chefs import JsonTreeChef
from ricecooker.classes.licenses import get_license
from le_utils.constants.languages import getlang  
from ricecooker.config import LOGGER
from ricecooker.utils.jsontrees import write_tree_to_json_tree

class NroerChannelJsonChef(JsonTreeChef):
	
	nroer_channel_tree = 'nroer_india_channel.json'
	
	def pre_run(self,args,options):
		
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
			self.data = json.load(f)
	def node_attributes(self,nroer_theme_tree):
		chef.open_file()
		for key in self.data:
			self.file_url = 'https://nroer.gov.in/api/v1?created_at='+ key
			url_obj = urllib.request.urlopen(self.file_url)
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
			node_file = urlopen(self.file_url)
			soups = BeautifulSoup(node_file, 'html.parser')
			p_tag = soups.find('p')
			topic_description = p_tag.text.strip('\\n')
			nroer_topic_node['description'] = topic_description

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
		node_expression = re.compile('= (.*)\\n*;')
		search_html = node_expression.search(html_data)
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
		file_node = urlopen(self.file_url)
		soups = BeautifulSoup(file_node, 'html.parser')
		p_tag = soups.find('p')
		file_description = p_tag.text.strip('\\n')
		nroer_file_node = dict (
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
		nroer_file_node['files'].append(file_dict)	
		if (self.type=="application/pdf"):
			nroer_file_node.update(kind = content_kinds.DOCUMENT)
			file_dict.update(file_type = content_kinds.DOCUMENT)
		elif (self.type=="video/mp4"):
			nroer_file_node.update(kind = content_kinds.VIDEO)
			file_dict.update(file_type = content_kinds.VIDEO)
		elif (self.type=="audio/mpeg"):
			nroer_file_node.update(kind = content_kinds.AUDIO)
			file_dict.update(file_type = content_kinds.AUDIO)
		else:
			print('kind not supported')
		nroer_file_node = self.extract_json_from_html(nroer_file_node)
		nroer_file_node = self.find_prior_node_in_theme_topics(nroer_theme_tree,nroer_file_node)
		
	def find_prior_node_in_theme_topics(self,nroer_theme_tree,nroer_file_node):
		for theme_item in nroer_theme_tree['children']:
			if theme_item['source_id'] in nroer_file_node['prior_node_id']:
				theme_item = self.append_child(nroer_theme_tree,nroer_file_node)
			else:
				self.find_prior_node_in_theme_item_topics(theme_item,nroer_file_node)
		return nroer_theme_tree
		
	def find_prior_node_in_theme_item_topics(self,theme_item,nroer_file_node):
		for topic_item in theme_item['children']:
			if topic_item['source_id'] in nroer_file_node['prior_node_id']:
				topic_item = self.append_child(topic_item,nroer_file_node)
			else:
				self.find_prior_node_in_topics(topic_item,nroer_file_node)
		
	def find_prior_node_in_topics(self,topic_item,nroer_file_node):
		for topic in topic_item['children']:
			if topic['source_id'] in nroer_file_node['prior_node_id']:
				topic = self.append_child(topic,nroer_file_node)
	
	def append_child(self,nroer_theme_tree,nroer_topic_node):
		"""Function to append all kind of nodes into tree"""
		nroer_theme_tree['children'].append(nroer_topic_node)
		return nroer_theme_tree
		
if __name__ == '__main__':
    chef = NroerChannelJsonChef()
    chef.main()