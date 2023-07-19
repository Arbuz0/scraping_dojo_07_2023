from src.scraper import QuoteScraper
from dotenv import load_dotenv
import os


def main() -> None:
    load_dotenv()
    
    url = os.environ.get('INPUT_URL')
    file = os.environ.get('OUTPUT_FILE')
    proxy = os.environ.get('PROXY')
    
    qs = QuoteScraper(url, file, proxy)
    qs.run()


if __name__ == '__main__':
    main()
