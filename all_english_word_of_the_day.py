#!/usr/bin/python

from lxml import html
import requests
import sqlite3 as db
import re
from random import randint
from time import sleep

def get_word_of_the_day_page(url):
	page = requests.get(url)
	html_tree = html.fromstring(page.content)
	return html_tree

class WordOfTheDay(object):
	def parse_html_tree(self, html_tree):
		word = html_tree.xpath('//div[@id="site"]/div[3]/div[1]/div[2]/div[1]/p[1]/text()')
		self.word = word[0]
		self.definition = return_string(html_tree.xpath('//div[@id="site"]/div[3]/div[1]/div[2]/div[1]/table[1]/tr[1]/td[2]/node()')) 
		self.example = return_string(html_tree.xpath('//div[@id="site"]/div[3]/div[1]/div[2]/div[1]/table[1]/tr[2]/td[2]/node()')) 
		self.translation = return_string(html_tree.xpath('//div[@id="site"]/div[3]/div[1]/div[2]/div[1]/table[1]/tr[3]/td[2]/node()'))
		self.word_id = self._parse_word_id(html_tree.xpath('//div[@id="site"]/div[3]/div[1]/div[2]/div[1]/text()'))
	
	def get_word(self):
		return self.word

	def get_example(self):
		return self.example

	def get_translation(self):
		return self.translation

	def get_whole_definition(self):
		return {"word":self.word, "definition":self.definition, "example":self.example, "translation":self.translation, "id":self.word_id}

	def get_data_in_tuple(self):
		return (self.word, self.definition, self.example, self.translation, self.word_id)

	def get_id(self):
		return self.word_id

	def _parse_word_id(sekf, chars_list):
        	word = [re.search(r'#(?P<id>\d+)', chars) for chars in chars_list if "#" in chars]
        	if isinstance(word, list):
                	return word[0].group("id")
        	else:
                	return word.group("id")

	def __str__(self):
		text_definition = u"Word of the day:\t{word}\nDefinition:\t\t{definition}\nExample:\t\t{example}\nPolish Translation:\t{translation}".format(word=self.word, definition=self.definition, example=self.example, translation=self.translation)
		return text_definition


class Phrasal(object):
	def parse_html_tree(self, html_tree):
		phrasal = html_tree.xpath('//div[@id="site"]/div[3]/div[1]/div[2]/div[1]/p[2]/text()')
		self.phrasal = phrasal[0]
		self.example = return_string(html_tree.xpath('//div[@id="site"]/div[3]/div[1]/div[2]/div[1]/table[2]/tr[1]/td[2]/node()'))
		self.translation = return_string(html_tree.xpath('//div[@id="site"]/div[3]/div[1]/div[2]/div[1]/table[2]/tr[2]/td[2]/node()'))
		self.phrasal_id = self._parse_phrasal_id(html_tree.xpath('//div[@id="site"]/div[3]/div[1]/div[2]/div[1]/text()'))

	def get_phrasal(self):
		return self.phrasal

	def get_example(self):
		return self.example

	def get_translation(self):
		return self.translation

	def get_whole_definition(self):
		return {"phrasal":self.phrasal, "example":self.example, "translation":self.translation, "id":self.phrasal_id}

	def get_data_in_tuple(self):
		return (self.phrasal, self.example, self.translation, self.phrasal_id)

	def get_id(self):
		return self.phrasal_id

	def _parse_phrasal_id(self, chars_list):
        	phrasal_id = [re.search(r'#(?P<id>\d+)', chars) for chars in chars_list if "#" in chars]
        	if isinstance(phrasal_id, list):
                	return phrasal_id[0].group("id")
        	else:
                	return phrasal_id.group("id")

	def __str__(self):
		text_definition = "Phrasal:\t\t{phrasal}\nExample:\t\t{example}\nPolish Translation:\t{translation}".format(phrasal=self.phrasal, example=self.example.encode('utf-8'), translation=self.translation.encode('utf-8'))
                return text_definition



def create_db(connection):
	with connection:
		connection.execute('''CREATE TABLE word (word text, definition text, example text, translation text, serial_id integer)''')
		connection.execute('''CREATE TABLE phrasal_verb (phrasal text, example text, translation text, serial_id integer)''')

def return_string(element):
	if not len(element):
		return ""

	if type(element) == type(list()):
		element = element[0]

	if isinstance(element, basestring):
                return element
        else:
                return element.text_content()

def get_word_id(html_tree):
	chars_list = html_tree.xpath('//div[@id="site"]/div[3]/div[1]/div[2]/div[1]/text()')
	word = [re.search(r'#(?P<id>\d+)', chars) for chars in chars_list if "#" in chars]
	if isinstance(word, list):
		return word[0].group("id")
	else:
		return word.group("id")

def get_word_of_the_day_and_phrasal(id_number=None):
	words_to_insert = list()
	phrasals_to_insert = list()
	html_trees = list()

	if id_number is None:
		# get latest
		url = 'http://www.ang.pl/word-of-the-day/today/'
		
                html_trees.append(get_word_of_the_day_page(url))

	elif id_number == 0:
		# get all
		url = 'http://www.ang.pl/word-of-the-day/today/'
                html_tree = get_word_of_the_day_page(url)
		word_of_day = WordOfTheDay()
                word_of_day.parse_html_tree(html_tree)
                phrasal = Phrasal()
                phrasal.parse_html_tree(html_tree)
                words_to_insert.append(word_of_day.get_data_in_tuple())
                phrasals_to_insert.append(phrasal.get_data_in_tuple())

		latest_word_id = word_of_day.get_id()
		for word_id in reversed(range(1 ,int(latest_word_id) - 1)):
	#	for word_id in reversed(range(1 , 3)):
			sleep(randint(0,1))
			url = 'http://www.ang.pl/word-of-the-day/archiwum/{number}'.format(number=word_id)
                	try:
				html_trees.append(get_word_of_the_day_page(url))
			except:
				with open("failed_to_download.txt", "w+") as fh:
					fh.write(url + "\n")
	else:
		# get particular result
		url = 'http://www.ang.pl/word-of-the-day/archiwum/{number}'.format(number=id_number)
                html_trees.append(get_word_of_the_day_page(url))

	for html_tree in html_trees:
		word_of_day = WordOfTheDay()
        	word_of_day.parse_html_tree(html_tree)
        	phrasal = Phrasal()
        	phrasal.parse_html_tree(html_tree)
		words_to_insert.append(word_of_day.get_data_in_tuple())
		phrasals_to_insert.append(phrasal.get_data_in_tuple())

	return words_to_insert, phrasals_to_insert


if __name__ == "__main__":
	words_to_insert, phrasals_to_insert = get_word_of_the_day_and_phrasal(0)
	with db.connect("test3.sqlite3") as connection:
		create_db(connection)
		c = connection.cursor()
		c.executemany('INSERT INTO word VALUES (?,?,?,?,?)', words_to_insert)
		c.executemany('INSERT INTO phrasal_verb VALUES (?,?,?,?)', phrasals_to_insert)

