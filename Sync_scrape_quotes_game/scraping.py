from bs4 import BeautifulSoup
import pathlib
import uuid
from csv import *
import requests
import re
import pickle
import datetime


fullBiography = {}


class ScrapeQuotes:
	def __init__(self, link=None):
		self.folder = self.create_folder()
		self.link = link
		self.count = 1
		self.page = '/page/'
		self.file = None

		headers = ['Author', 'Quote', 'Tags', 'Link about']

		temp_name = f"{self.folder}/{str(uuid.uuid4())}.csv"
		with open(temp_name, 'w') as file:
			self.writer = DictWriter(file, fieldnames=headers)
			self.writer.writeheader()
			self.file = temp_name

	@property
	def link(self):
		# return f"Scrape data from {self.link}"
		return self._link

	@link.setter
	def link(self, value):
		if value is None:
			self._link = 'http://quotes.toscrape.com'
		else:
			self._link = value
	
	def create_folder(self):
		directory = pathlib.Path.cwd()
		return pathlib.Path(f"{directory}/scraped_data").mkdir(exist_ok=True) \
			   if pathlib.Path(f"{directory}/scraped_data").mkdir(exist_ok=True) \
			   is not None else f"{directory}/scraped_data"

	def get_site(self, num, temp=None):
		if num == 1:
			return requests.get(self.link+self.page+str(self.count)).text
		elif num == 2:
			return requests.get(temp).text.strip()

	def start_scrape(self):
		site = self.get_site(1)
		self.soup = BeautifulSoup(site, 'lxml')

		while self.soup.find('li', class_='next'):
			self.scrape_quotes()
			self.count += 1
			site = self.get_site(1)
			self.soup = BeautifulSoup(site, 'lxml')

		# means last page
		self.scrape_quotes()

	def getFullBio(self, url):
		site = self.get_site(2, url)
		self.soup = BeautifulSoup(site, 'lxml')
		return self.soup.find('div', class_='author-description').get_text()

	def scrape_quotes(self):
		allQuotes = self.soup.find_all('div', class_='quote')

		for quote in allQuotes:
			mainText = quote.find('span', class_='text').text.strip()
			author = quote.find('small', class_='author').text.strip()

			about = quote.find(attrs={'class': None}).a['href']
			about_url = self.link + about

			self.bio = self.getFullBio(about_url)

			full_name = author

			if len(author.split()) <= 2:
				name, surname = author.split()
			else:
				name = author.split()[0]
				surname = author.split()[2]

			substring = [surname, name, full_name]

			while len(substring) != 0:
				self.bio = re.sub(fr"{substring[-1]}", 'Unknown', self.bio)
				substring.pop()

			if author not in fullBiography:
				fullBiography[author] = [self.bio]

			# tags = map(lambda tag: tag.a['href'], quote.find_all(class_='tags'))

			try:
				for tag in quote.find_all(class_='tags'):
					tag = tag.a['href']
					tag_url = self.link + ''.join(tag)

					with open(self.file, 'a', encoding='utf-8', newline='') as fl:
						csv_writer = writer(fl)
						csv_writer.writerow([author, mainText, tag_url, about_url])

			except TypeError:
				continue
