import argparse
import time
import pathlib
from random import choice, randint
import os
import csv
from bs4 import BeautifulSoup
import requests
from Async_scraping import ScrapeQuotes, fullBiography
import asyncio
import aiohttp
import datetime
from concurrent.futures import ThreadPoolExecutor as Executor
import uvloop


# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

hints = 0


class Game:

	def __init__(self, hard):
		self.hard = hard
		self.directory = pathlib.Path.cwd()
		self.files = f"{self.directory}/scraped_data"

		for root, dir, files in os.walk(self.files):
			if '.DS_Store' in files:
				files.remove('.DS_Store')
			allFiles = [os.path.join(root, x) for x in files]
			self.file = choice(allFiles)


	def prepare_quote(self):
		with open(self.file, 'rt') as fl:
			csv_reader = csv.reader(fl)
			all_quotes = list(csv_reader)
			num = randint(1, len(all_quotes) - 1)
			self.author = all_quotes[num][0]
			self.quote = all_quotes[num][1]
			self.tag = all_quotes[num][2]
			self.about = all_quotes[num][3]

	async def hints(self):
		async with aiohttp.ClientSession() as session:
			async with session.get(self.about) as resp:
				resp.raise_for_status()

				site = await resp.text()

		soup = BeautifulSoup(site, 'lxml')

		self.birth = soup.find('span', class_='author-born-date').text.strip()
		self.place = soup.find('span', class_='author-born-location').text.strip()
		self.hint_one = f"{self.birth}-{self.place}"
		author_info = fullBiography[self.author]
		self.hint_two = author_info[: min(len(author_info), 50)]
		self.hint_three = self.author.split()[0]

	def hint_chooser(self, value):
		if value == 3:
			print(f"Your answer is incorrect. First hint: {self.hint_one}")
		elif value == 2:
			print(f"Your answer is incorrect. Second hint: {self.hint_two[0].strip()}")
		elif value == 1:
			print(f"Your answer is incorrect. Last hint: {self.hint_three}")
		return

	@classmethod
	def level(cls, num):
		return cls(num)

	async def ask_for_game(self):
		while True:
			user_answer = input('Do you want to play more?[y,n]: ').lower()
			if user_answer in ['y', 'n']:
				if user_answer == 'y':
					figure = input('Put your difficulty level (1, 2, 3, 4): ')
					while int(figure) > 4 or int(figure) <= 0:
						figure = input('Put your difficulty level (1, 2, 3, 4): ')
					return await main(self, lev=int(figure))
					# we return from called instance with result
					# and result is function to be called
				else:
					self.bye()
					break
			else:
				print('Please, input y/n (case insensitive)')
		return

	def bye(self):
		print('どうもありがとうございます')
		return


async def main(instance, lev=None):
	# to use current loop inside this function
	loop = asyncio.get_running_loop()

	await loop.run_in_executor(None, instance.prepare_quote)

	print('Who is the author of the quote?')
	print(instance.quote)

	# after one round, to 
	# put the .hard we are
	# to create some form of check
	if lev is not None:
		instance.hard = lev

	while instance.hard != 0:
		# put here as we need 
		# self.author in .hints()
		global hints
		if hints == 0:
			await instance.hints()
			hints = 1

		print('You answer is... ')

		answer = input().lower().strip()
		if answer == instance.author.lower().strip():
			print('すごい！ You win')
			return await instance.ask_for_game()
		else:
			instance.hard -= 1
			instance.hint_chooser(instance.hard)

	print('Game is over:(')

	return await instance.ask_for_game()


if __name__ == '__main__':
	t0 = datetime.datetime.now()

	# global loop
	loop = asyncio.get_event_loop()

	# if we need to do some CPU bound operations
	executor = Executor()
	loop.set_default_executor(executor)

	# put all scraping stuff inside conditions
	# so as to do it once.
	# At first do all the scraping as we need
	# the folder for picking a file
	scrape = 0
	if scrape == 0:
		scrapeObject = ScrapeQuotes()
		loop.run_until_complete(scrapeObject.start_scrape())
		scrape = 1

	# for first try use `argparse`
	# when not first try use lev
	parser = argparse.ArgumentParser(
		description="Guessing game where you can put level of difficulty (descending): 1, 2, 3")
	parser.add_argument('-l', '--level', help='your game level', default=4, type=int)

	args = parser.parse_args()
	game = Game.level(args.level)

	dt = datetime.datetime.now() - t0
	print(f'Done in {dt.total_seconds():.2f} sec.')

	task = loop.create_task(main(game))
	try:
		loop.run_until_complete(task)
	except KeyboardInterrupt:
		print('Program was cancelled')


	# to clean up if there are remaining tasks
	tasks = asyncio.all_tasks(loop=loop)
	if len(tasks) > 0:
		for t in tasks:
			t.cancel()

		group = asyncio.gather(*tasks, return_exceptions=True)
		loop.run_until_complete(group)
		executor.shutdown(wait=True)
		loop.close()
