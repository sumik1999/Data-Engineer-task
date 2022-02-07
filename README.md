# Data-Engineer

### In the script, **wiki_extractor.py** I have stored my output in *out.json*. The approach that i have taken to do this task is enlisted below.
1. The script is broken into functions. The first function called is *main*. Within main I have :
   - Used **[optparse module](https://docs.python.org/3/library/optparse.html)** in python to make command line options of  *--keyword*, *--num_urls* and *--output* available.
   - If options are provided the main function calls the *wikipedia_search* function with the query string
      
2. The *wikipedia_search* function will take the string and construct the url to request from wikipedia passing the query string as parameters in request.
   - In the url, the limit is also passed which was provided as --num_urls. Due to the passing of limit parameter, only that many number of search results appear.
   - **[requests](https://docs.python-requests.org/en/latest/)** module is used to send request and **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)** for parsing html
   - Request --> soup --> finding elements
   - For finding links, I have first found all divs that contain search results and then found
   
        1. Url from it's content by scraping the **href** attribute from that div's a tag, iterating over all divs.
        2. I have called the extract_data function on all the links scraped above.
        3. I have used **[Threadpool executor](https://docs.python.org/3/library/concurrent.futures.html)** for launching all requests parallely
        
3. The *extract_data* function will search all paragraphs within the url and return the **first** paragraph from each url that contains **characters**.
   - Regex matching is used here for finding paragraphs with words in it and not just blank spaces!
   - It then stores all results into a dictionary and then returns it
   - The returned dictionary is appended to a list and finally the list is passed on to json dump function from **[json](https://docs.python.org/3/library/json.html)** module to write to the filename passed in output parameters.
 
### In the script, **pdf_extractor.py** I have stored my sample output in *pdf_extract.json*. The approach that I have taken is enlisted below:
1. From the main function, I am calling the *excel_extract* function:

   - The excel file is extracted using **[openpyxl](https://openpyxl.readthedocs.io/en/stable/)** and it seperates links based on wheteher it ends in *.pdf* or not (Regex used)
   - The two kinds of links are stored and returns the arrays
2. Then from *main*, I'm calling the *pdf_extract_already_link* for every known pdf link:
   - It takes the url, as both page and pdf url are same, stores them in a dictionary
   - I have received the response content by sending a request on the pdf url and written the content of it to the file using **write_bytes**
   - the pdf file gets created on fly 
   - I have then called the *convert_pdf* function to convert the data of each pdf
3. In the *convert_pdf* function, the pdf filepath is taken:
   - Using **[pdf2image](https://pdf2image.readthedocs.io/en/latest/)** module,each pdf is split into images 
   - Each image is then passed through ***[pytesseract](https://pypi.org/project/pytesseract/)**.convert_to_string* function using the langugage parameter as *marathi (mar)*.
   - This above *function* takes Pillow images and converts them using ocr to strings (inbuilt)
   - The image gets converted to string and is stored
   - The function returns all the extracted string data, stripped of newlines and combined together, from an individual pdf
   
4. From the *main* function, *get_links_for_unavailable* function is called on the second category of links.
   - It constructs the url for each received link by from where the pdf can be downloaded
   - It uses regex to do so
   - It first hits archive.org/download/filename
   - Then from it's available urls sees which url is ending in **.pdf** and scrapes that url and returns
5. From *main* function, *pdf_extract_newlink* is called for all now available urls:
   - This function will get two different urls page and pdf and store accordingly
   - This function calls *extract_pdf* too for pdf extraction
   - It returns the info for the remaining urls
   
6. From *main* function, results from both kind of links are added and stored into the json file *pdf_extract.json*
#### Due to large file size, I have uploaded only a sample of the pdf_extractor in *pdf_extract_sample.json*


#### For replicating these results:
1. Clone this repo using `git clone https://github.com/sumik1999/wiki-pdf-extraction.git`
2. You must have tesseract and marathi language's data installed on your system. To do so in ubuntu run
 ` sudo apt-get install tesseract-ocr` and then to install marathi run
` sudo apt-get install tesseract-ocr-mar`
3. To install the requirements run
 `pip install -r requirements.txt`
4. Run `cd wiki-pdf-extraction/`
5. Run `python wiki_extractor.py --keyword=<your query string> --num_urls=<number of urls to scrape> --output=<Name of output file>`
6. Run `python pdf_extractor.py` to get the pdf_Extract.json
   
   
