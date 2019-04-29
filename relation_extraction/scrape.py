from bs4 import BeautifulSoup
import requests
import sys

def read_page(url):
    url_title = url[url.rfind('wiki')+5:]
    myFile = open('data/raw_data.txt', 'w', encoding="utf-8")
    print("reading page: " + url_title)
    page = requests.get(url)
    try:
        soup = BeautifulSoup(page.text, "html5lib")
        text = soup.find("div",{"class": "mw-parser-output"})
        full_text = ""
        toc = text.find("div", {"class": "toc"})
        for t in toc.previous_siblings:
             if not t.find('img') and (t.name == 'p' or t.name == 'ul'):
                full_text += str(t.getText().replace('\n', ' '))
        myFile.write(full_text + "\n")
    except AttributeError:
        print("invalid page, skipping")

if __name__ == '__main__':
    page_url = str(sys.argv[1])
    read_page(page_url)
    print('Scraping Complete.')
