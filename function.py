import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import unicodedata
import re

# define a class for scrapping Google Scholar
class ScrapGScholar:
    def __init__(self, query, max_pages=2):
        self.query = query
        self.max_pages = max_pages
        self.base_url = "https://scholar.google.com/scholar"
        self.params = {
            "q": query,
            "hl": "en",
        }
        self.results = []
        self.page_count = 0
        self.next_page_url = None
        self.dataset = None

    # feeding query to start searching
    def start_searching(self):
        '''
        This function starts the searching process by sending requests to 
        Google Scholar and parsing the results.
        '''
        while self.page_count < self.max_pages:
            # first page
            if self.page_count == 0:
                response = requests.get(self.base_url, params=self.params)
            
            # after the first page, next page url leads to the contents
            else:
                response = requests.get(self.next_page_url)            
            response.raise_for_status()
            response.encoding = 'utf-8' 
            soup = BeautifulSoup(response.text, "html.parser")
            result_docs = soup.find_all("div", class_="gs_r gs_or gs_scl")
            
            # grab result from one page
            self.grab_results_from_one_page(result_docs)        

            # find the next-page URL    
            self.next_page_url = self.get_next_url(soup)
            if not self.next_page_url:
                break
            self.page_count += 1

            # Add sleep to pause between requests
            time.sleep(10)             
        return self.results

    def grab_results_from_one_page(self, result_docs):
        '''
        This function processes the result_docs from one page to extract the 
        title, link, author, year, journal, and publisher.
        '''
        for doc in result_docs:
          # process nodes to find tags ands save their values
            title_doc = doc.find("h3", class_="gs_rt")
            title = self.clean_text(title_doc.get_text() if title_doc else "N/A")
            
            link_doc = title_doc.find("a") if title_doc else None
            link = link_doc["href"] if link_doc else "N/A"
            
            author_year_doc = doc.find("div", class_="gs_a")
            author_year_text = author_year_doc.get_text() if author_year_doc else "N/A"
            
            abstract_doc = doc.find("div", class_="gs_rs")
            abstract = self.clean_text(abstract_doc.get_text() if abstract_doc else "N/A")
            
            author, year, journal, publisher = self.seperate_author_year(author_year_text)
            
            self.results.append({
                "title": title,
                "link": link,
                "author": author,
                "year": year,
                "journal": journal,
                "publisher": publisher,
                #"abstract": abstract,
                #"author_year_text": author_year_text
            })
    
    def seperate_author_year(self, author_year_text):
        '''
        This function separates the author, year, journal, and publisher 
        from the author_year_text.
        There is a chance that the paper has no journal or publisher
        '''
        parts = author_year_text.split("- ")
        author = parts[0].strip() if len(parts) > 0 else "N/A"
        journal = parts[1].strip().split(", ")[0] if len(parts) > 1 else "N/A"
        year = parts[1].strip().split(", ")[1].strip() if len(parts) > 1 and len(parts[1].strip().split(",")) > 1 else "N/A"
        publisher = parts[2].strip() if len(parts) > 2 else "N/A"
        
        # Check if journal contains a valid year
        if journal.isdigit() and year == "N/A":
            year = journal
            journal = "N/A"

        return self.clean_text(author), year, self.clean_text(journal), publisher

    def get_next_url(self, soup):
        '''
        This function finds the URL of the next page.
        '''
        next_span = soup.find('span', class_='gs_ico gs_ico_nav_next')
        if next_span and next_span.parent.name == 'a':
            next_url = f"https://scholar.google.com{next_span.parent['href']}"
            return next_url
        return None

    def clean_text(self,text):
        """
        Normalize the text and remove non-numerical or non-alphabetical symbols.
        clean all the context that contains unreadable ASCIIs
        """
        normalized_text = unicodedata.normalize('NFC', text)

        # remove anything that is in between []
        cleaned_text = re.sub(r'\[.*?\]', '', normalized_text)

        # Use regex to remove non-numerical or non-alphabetical characters
        cleaned_text = re.sub(r'[^a-zA-Z0-9\s!@#$%^&*(),.?":{}|<>—-]', '', cleaned_text)
        
        # Return the cleaned text
        return cleaned_text.strip()

    def write_to_csv(self,filename = "scholar_results.csv"):
        self.dataset = pd.DataFrame(self.results)
        self.dataset.to_csv(filename, index=False, encoding='utf-8')  # Ensure UTF-8 encoding
        return self.dataset