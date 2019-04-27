from bs4 import BeautifulSoup
import requests

def read_page(url):
    url_title = url[url.rfind('wiki')+5:]
    myFile = open('./' + url_title + '_raw_data.txt', 'w', encoding="utf-8")
    print("reading page: " + url_title)
    page = requests.get(url)
    try:
        soup = BeautifulSoup(page.text, "html5lib")
        text = soup.find_all('p')
        full_text = ""
        title = soup.find('h1').getText() + "\n"
        for t in text:
             if not t.find('img') and (t.name == 'p' or t.name == 'ul'):
                full_text += str(t.getText().replace('\n', ''))
        #myFile.write(title)
        myFile.write(full_text + "\n")
    except AttributeError:
        print("invalid page, skipping")
    return full_text

if __name__ == '__main__':
    page_url = str(sys.argv[1])
    a = read_page(page_url)
    print('Scraping Complete.')
