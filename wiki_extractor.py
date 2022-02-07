import requests
from bs4 import BeautifulSoup
import optparse
import re
import json
from concurrent.futures import ThreadPoolExecutor

"https://en.wikipedia.org/w/index.php?search=Indian+Historical+Events&title=Special:Search&profile=advanced&fulltext=1&ns0=1"

def extract_result_data(url):
    """This function goes to each individual scraped url and scrapes a paragraph from each one"""
    dict_info = {}
    print("executing",url)
    url_page_req = requests.get("https://en.wikipedia.org"+url)
    dict_info["url"] = url_page_req.url
    soup_page = BeautifulSoup(url_page_req.content, 'html.parser')
    paragraphs = soup_page.findAll("p")
    for para in paragraphs:
        if re.findall("w+",para.get_text()):
            dict_info["paragraph"] = para.get_text()
            break

    return dict_info


def wikipedia_search(keyword,num_urls,savefilename):
    """This function search wikipedia for the given keywords and scrapes the urls of the obtained results"""
    
    req = requests.get("https://en.wikipedia.org/w/index.php?",params={"search": keyword,"limit":num_urls})
    soup = BeautifulSoup(req.content, 'html.parser')
    print(req.url)
    
    list_div = soup.findAll("div",attrs={"class":"mw-search-result-heading"})
    
    urls = [div.find("a")['href'] for div in list_div]
    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        results = list(executor.map(extract_result_data,urls))        

    with open(savefilename,'w') as file:
        json.dump(results,file,indent=4)


def main():
    """This function creates command line options and takes input"""
    parser = optparse.OptionParser()
    parser.add_option("--keyword",type='string',help="Takes the input keywords to search on wikipedia",dest="keyword")
    parser.add_option("--num_urls",type='int',help="Takes the number of pages to scrape",dest="num_pages")
    parser.add_option("--output",type='string',help="Takes the name of output json file to store in",dest="output_json")
    (options, args) = parser.parse_args()

    if not options:
        print ("Please provide options!")
        exit(0)
    else:
        keyword = options.keyword
        wikipedia_search(keyword=options.keyword,savefilename=options.output_json,num_urls=options.num_pages)



if __name__ == "__main__":
    main()
