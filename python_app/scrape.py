from bs4 import BeautifulSoup
import requests

def read_page(url):
    page = requests.get(url)
    try:
        soup = BeautifulSoup(page.text, "html5lib")
        text = soup.find("div",{"class": "mw-parser-output"})
        full_text = ""
        toc = text.find("div", {"class": "toc"})
        for t in toc.previous_siblings:
             if not t.find('img') and (t.name == 'p' or t.name == 'ul'):
                full_text = str(t.getText().replace('\n', ' ')) + full_text
    except AttributeError:
        print("invalid page, skipping")
    return full_text
