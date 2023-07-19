import requests
import re
import json
import dataclasses
import logging

from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class Quote():
    text: str
    by: str
    tags: list[str]


class QuoteScraper:
    def __init__(self, input_url: str, output_file: str, proxy: str) -> None:
        self.input_url = input_url
        self.output_file = output_file
        self.proxy = proxy
    
    def run(self) -> None:
        self.clear_export_file()
        next_url = self.input_url
        
        while next_url:
            quotes, next_url = self.scrape_page(next_url)
            
            if quotes:
                self.export_to_file(quotes)
            
    def scrape_page(self, url: str) -> tuple[Quote | None, str | None]:
        response = requests.get(url, proxies=self.get_proxies())
        
        if response.status_code != 200:
            logging.error(f'Url: { url }, Ststus Code: {response.status_code}')
            return (None, None)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        quotes = self.extract_quotes(soup)
        next_url = self.extract_next_url(soup)
        
        return (quotes, next_url)
            
    def extract_quotes(self, soup: BeautifulSoup) -> list[Quote] | None:
        script_elements = soup.find_all('script')
        
        if len(script_elements) < 2:
            logging.warn('Page does not contain required information.')
            return None
        
        javascript_code = script_elements[1].text
        
        data_pattern = r'var data = (\[.*?\]);'
        match = re.search(data_pattern, javascript_code, re.DOTALL)
        
        if match:
            data_json = match.group(1)
            try:
                data_dict = json.loads(data_json)
                
                result = []
                for entry in data_dict:
                    text = entry['text'][1:-1]
                    author = entry['author']['name']
                    tags = entry['tags']
                    
                    result.append(Quote(text, author, tags))
            except:
                logging.warn(f'Invalid format: { data_json }')
                result = None
                
        else:
            result = None
        
        return result
    
    def extract_next_url(self, soup: BeautifulSoup) -> str | None:
        next_element = soup.find('li', {'class': 'next'})
        next_anchor = next_element.find('a') if next_element else None
        relative_url = next_anchor.get('href') if next_anchor else None
        
        return urljoin(self.input_url, relative_url) if relative_url else None
        
    def clear_export_file(self) -> None:
        with open(self.output_file, 'w') as f:
            pass
    
    def export_to_file(self, quotes: list[Quote]) -> None:
        with open(self.output_file, 'a', encoding='utf-8') as f:
            for qte in quotes:
                qte_json = json.dumps(dataclasses.asdict(qte), ensure_ascii=False)
                f.write(qte_json)
                f.write('\n')
                
    def get_proxies(self) -> dict:
        return {'http': f'http://{ self.proxy }', 'https': f'http://{ self.proxy }'}
                