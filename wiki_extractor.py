import requests
from bs4 import BeautifulSoup
import optparse
import re
import json

"https://en.wikipedia.org/w/index.php?search=Indian+Historical+Events&title=Special:Search&profile=advanced&fulltext=1&ns0=1"

def wikipedia_search(keyword,num_urls,savefilename):
    
    req = requests.get("https://en.wikipedia.org/w/index.php?",params={"search": keyword,"limit":num_urls})
    soup = BeautifulSoup(req.content, 'html.parser')
    print(req.url)
    
    list_div = soup.findAll("div",attrs={"class":"mw-search-result-heading"})
    list_info = []
    for div in list_div:

        dict_info = {}
        url_next = div.find("a")['href']
        url_page_req = requests.get("https://en.wikipedia.org"+url_next)
        dict_info["url"] = url_page_req.url
        soup_page = BeautifulSoup(url_page_req.content, 'html.parser')
        paragraphs = soup_page.findAll("p")
        for para in paragraphs:
            if re.findall("[a-zA-Z]",para.get_text()):
                dict_info["paragraph"] = para.get_text()
                break
        list_info.append(dict_info)

    with open(savefilename,'w') as file:
        json.dump(list_info,file,indent=4)





if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("--keyword",type='string',help="Takes the input keywords to search on wikipedia",dest="keyword")
    parser.add_option("--num_urls",type='int',help="Takes the number of pages to scrape",dest="num_pages")
    parser.add_option("--output",type='string',help="Takes the name of output json file to store in",dest="output_json")
    (options, args) = parser.parse_args()

    if not options:
        print (parser)
        exit(0)
    else:
        keyword = options.keyword
        wikipedia_search(keyword=options.keyword,savefilename=options.output_json,num_urls=options.num_pages)