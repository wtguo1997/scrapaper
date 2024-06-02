# Scrap Google Scholar

This is a Python script for scraping Google Scholar. 

## Installation

Before running the script, ensure you have the required packages installed. You can install `bs4` and other dependencies using pip:

```sh
pip install beautifulsoup4 requests pandas
```

Usage
After defining the query and max_pages, the script will scrape all papers and save the following details:

- Title
- Link
- Author
- Year
- Journal
- Publisher

Example:

```
from function import ScrapGScholar

# Define your search query and the number of pages to scrape
query = "Why cats love purrrrrr"
max_pages = 2

# Create an instance of the scraper
scraper = ScrapGScholar(query, max_pages)

# Start the search and get the results
results = scraper.start_searching()

# Save the results to a CSV file (default filename is "scholar_results.csv")
scraper.write_to_csv()
```

Make sure to comply with Google Scholar's terms of service when using this script.
