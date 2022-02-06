from ast import Pass
import requests
from urllib import request
from openpyxl import load_workbook
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import PyPDF2
import json
from bs4 import BeautifulSoup
from pdf2image import convert_from_path, 
import pytesseract
import sys


def convert_pdf(filename):
    """This function does the ocr rendering part.It takes in the name of the pdf file, converts it to images using pdf2image and then for each image,runs pytesseract on it to extract the data"""

    images = convert_from_path(filename)
    print(filename)
    data = []
    for index, image in enumerate(images):
        print(f"Working on....{index+1} image")
        data.append((pytesseract.image_to_string(
            image, lang='mar')).strip("\n "))
    print("data made!")
    return data


def pdf_extract_alreadylink(urls):
    """This is the function to make a pdf from the url given and from the .pdf extensions that already exists"""
    page_url, pdf_url = urls

    response = requests.get(page_url)
    file = Path(page_url.split("/")[-1])

    file.write_bytes(response.content)
    print("file Made!")
    info_dict = {}
    info_dict["page url"] = page_url
    info_dict["pdf url"] = pdf_url

    info_dict["pdf _content"] = "".join(convert_pdf(file))
    return info_dict


def pdf_extract_newlink(urls):
    """This is the function to make a pdf from the urls not given in the data sheet but was extracted from scraping"""
    page_url, pdf_url = urls

    response = requests.get(pdf_url)
    file = Path(pdf_url.split("/")[-1])

    file.write_bytes(response.content)
    print("New file Made!")
    info_dict = {}
    info_dict["page url"] = page_url
    info_dict["pdf url"] = pdf_url

    info_dict["pdf _content"] = "".join(convert_pdf(file))
    return info_dict


def get_links_for_unavailable(url):
    """This function scrapes pdf url information for unavailable pdfs and constructs the url from the given data. It looks for the first link that matches a .pdf extension, scrapes that , constructs the link and returns"""

    identifier = re.match(
        'https?:\/\/archive.org\/details\/([^\/]+)\/?', url).groups()[0]
    page_url = f'https://archive.org/download/{identifier}'
    resp = requests.get(page_url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    all_links = soup.findAll("a")

    for link in all_links:
        if re.search('.pdf$', str(link.string)):
            return page_url+'/'+link['href']


def excel_extract():
    """This function extracts data from the excel sheet given with the task and identifies available links and unavailable links and returns both"""

    data_file = 'Data Engineer Task.xlsx'
    wb = load_workbook(data_file)
    ws = wb['Data Engineer Task']
    all_rows = list(ws.rows)
    pdf_link_already_list = []
    pdflinks_to_search = []
    for row in all_rows:
        for cell in row:
            if re.search("pdf$", cell.value):
                pdf_link_already_list.append(str(cell.value))
            else:
                pdflinks_to_search.append(str(cell.value))
            break

    return pdf_link_already_list, pdflinks_to_search


def main():
    """This is the main function to call on excel_extract and all other functions as well as creates the required json file"""

    pdf_link_already_list, pdflinks_to_search = excel_extract()
    results1, results2, now_available = [], [], []
    for pdf in pdf_link_already_list:
        results1.append(pdf_extract_alreadylink((pdf, pdf)))

    for pdf in pdflinks_to_search:
        now_available.append(get_links_for_unavailable(pdf))

    for page, pdf in zip(pdflinks_to_search, now_available):
        results2.append(pdf_extract_newlink((page, pdf)))

    results = results1.extend(results2)
    with open("pdf_extract.json", "w") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
