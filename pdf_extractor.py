from ast import Pass
import requests
from urllib import request
from openpyxl import load_workbook
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
from bs4 import BeautifulSoup
from pdf2image import convert_from_path, convert_from_bytes 
import tempfile
import pytesseract
import sys


def convert_pdf(filename):

    images = convert_from_path(filename)
    print(filename)
    data = []
    index = 1
    for image in images:
        print(f"Working on....{index} image")
        data.append(pytesseract.image_to_string(image,lang='mar'))
        index+=1
    print("data made!")
    return data

def pdf_extract_alreadylink(urls):
    print(urls)
    page_url , pdf_url = urls

    response = requests.get(page_url)
    file = Path(page_url.split("/")[-1])

    file.write_bytes(response.content)
    print("file Made!")
    info_dict={}
    info_dict["page url"] = page_url
    info_dict["pdf url"] = pdf_url


    info_dict["pdf _content"] = "".join(convert_pdf(file))
    return info_dict

def pdf_extract_newlink(urls):
    print(urls)
    page_url , pdf_url = urls

    response = requests.get(pdf_url)
    file = Path(pdf_url.split("/")[-1])

    file.write_bytes(response.content)
    print("New file Made!")
    info_dict={}
    info_dict["page url"] = page_url
    info_dict["pdf url"] =pdf_url


    info_dict["pdf _content"] = "".join(convert_pdf(file))
    return info_dict

def get_links_for_unavailable(url):

    identifier = re.match('https?:\/\/archive.org\/details\/([^\/]+)\/?',url).groups()[0]
    page_url = f'https://archive.org/download/{identifier}'
    resp = requests.get(page_url)
    soup = BeautifulSoup(resp.content,'html.parser')
    all_links = soup.findAll("a")
    
    for link in all_links:
        if re.search('.pdf$',str(link.string)):
            return page_url+'/'+link['href']
        

def excel_extract():

    data_file = 'Data Engineer Task.xlsx'
    wb = load_workbook(data_file)
    ws = wb['Data Engineer Task']
    all_rows = list(ws.rows)
    pdf_link_already_list =[]
    pdflinks_to_search = []
    for row in all_rows:
        for cell in row:
            if re.search("pdf$",cell.value):
                pdf_link_already_list.append(str(cell.value))
            else:
                pdflinks_to_search.append(str(cell.value))
            break 

    results1 , results2 , now_available = [] ,[],[]
    for pdf in pdf_link_already_list:
        results1.append(pdf_extract_alreadylink((pdf,pdf)))
    
    with open("pdf_extract.json","w") as file:
        json.dump(results1,file,indent=4,ensure_ascii=False)

    for pdf in pdflinks_to_search:
        now_available.append(get_links_for_unavailable(pdf))

    for page,pdf in zip(pdflinks_to_search,now_available):
        results2.append(pdf_extract_newlink((page,pdf)))

    results = results1.extend(results2)   

    with open("pdf_extract.json","a") as file:
        json.dump(results2,file,indent=4,ensure_ascii=False)


if __name__=="__main__":
    excel_extract()
