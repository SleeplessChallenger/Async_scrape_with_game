<h2>Scraping project with game</h2>

1. In this project I did scraping of `http://quotes.toscrape.com` with the help of `Beautiful Soup` where I extracted:
- quote
- author
- link with author's history
- tags of the quote
- full bio of the author with author's name replaced by using `regex`

and all of this stuff get dumped into `.csv` file, example of which you can see in
`scraped_data` folder.

2. Second part is the game, where, at first, user can specify desired level of difficulty
(simply typing integer in CLI), otherwise default number is used.

<hr>
<h4>Process:</h4>
  User will be presented with a quote and if the input of the user is correct (<ins><i>case insensitive</i></ins>),
  then the game will suggest another round. If the answer isn't correct, then the user will have
  particular amount of hints, based on the level of difficulty. Regardless of the result, game will
  ask for another round and also ask to specify level of difficulty.
<hr>

<h3>Different versions</h3>

1. Files without a folder are the **main version** where I used `AsyncIO`, `aiohttp` to elevate the speed. `scraped_data`
  is a folder with example of scraped data.
  
2. Files in a folder, named `Sync_scrape_quotes_game`, resemble all written above, but they use
   `bs4` without any <ins>async</ins> features.

- Actual difference in time between `sync` and `async` versions may reach up to 6 times.
- all required folders & files will be created dynamically
