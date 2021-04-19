import pandas as pd
import numpy as np
import requests
#import re
import regex
import PyPDF2
import logging
import glob, os
import fitz   #PyMuPDF
from datetime import datetime, date



workingdir = "/home/admin/dockers/masters/app/"
csv_dir = "/home/admin/dockers/masters/data/csv/"
logs_dir = "/home/admin/dockers/masters/data/pdfminer/logs/"
files_dir = "/home/admin/dockers/masters/data/downloads/"
text_dir = "/home/admin/dockers/masters/data/pdfminer/text/"
search_dir = "/home/admin/dockers/masters/data/pdfminer/search/"

# Note single words e.g. 'WATER' must be at the end of the list
water_sections =['SOIL AND WATER',\
                'SOIL & WATER',\
                'SURFACE WATER',
                'WATER QUALITY',\
                'WATER MANAGEMENT',\
                'WATER',\
                'Water Management and Monitoring',\
                '4. Water Management',\
                'SURFACE AND GROUND WATER',\
                'SURFACE & GROUND WATER'    ]

next_sections = ['REHABILITATION MANAGEMENT',\
                'BIODIVERSITY',\
                'REHABILITATION',\
                'HERITAGE',\
                'NOISE AND VIBRATION',\
                'Hazardous Materials and Tailings Management',\
                'LANDSCAPE MANAGEMENT',\
                'HAZARDOUS',\
                'Air Quality, Blast',\
                'FAUNA & FLORA',\
                'FAUNA AND FLORA',   
                'AIR QUALITY']


def setupLogging(dest_dir=None):

    if dest_dir is None:
        dest_dir = os.path.realpath(logs_dir)
    
    logfile = logs_dir + str(datetime.now().strftime('%Y%m%d%H%M%S')) + ".log"
    logging.basicConfig(filename=logfile,level=logging.INFO)
    logging.info('-' * 80)
    logging.info(' extract_groundwater_cond1.3.py Logging started at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))



def write_text(pdf,all_text):
    fname = os.path.basename(pdf)
    tname = text_dir + fname[:-3] + "txt"

    text_filename = open(tname, "wt")
    text_filename.write(all_text)

    text_filename.close()
    logging.info(' TEXT: ' + tname + ' created')
    return True  # need to check status of file      



def write_pages(pdf,search_text):
    
#    print(search_text)
    fname = os.path.basename(pdf)
    tname = search_dir + fname[:-3] + "txt"

#    doc = fitz.open(pdf)
    text_filename = open(tname, "wt")
    
    text_filename.write(search_text)
    text_filename.close()
    



def consolidate_pages(pdf,pg):

    alltext = ""
    print(pg)
    doc = fitz.open(pdf)
    for i in range((pg[0] - 1), pg[1]):
     
        text = doc.get_page_text(i)
        alltext = alltext + text

    doc.close()
    return alltext



def search_text(pdf,alltext,bookends):

    if bookends[0] != "" and bookends[1] != "":
        pattern = '(?<=[\d\s]*\\n' + bookends[0] + ').*(?=' + bookends[1] + ')' 
#        pattern = '(?<=\\n' +bookend1 + ')[\d\s]*[\.]*[\d\s]*(?=\\n' + bookend2 + ')[\d\s]*[\.]*[\d\s]*'
        print(f"PDF: {pdf}, Pattern: {pattern}")
        logging.info(' PDF: ' + pdf + ' Extracting text using search pattern ' + pattern + '')
        conditions_pattern = regex.compile(pattern, regex.DOTALL)    
        conditions_search = conditions_pattern.search(alltext)

        print(conditions_search)
        if (conditions_search == None):
            logging.info(' ERROR PDF: ' + pdf + ' Couldn\'t find pattern ' + pattern + ' in text')
            return False

        logging.info(' PDF: ' + pdf + ' search result is ' + str(conditions_search) + ' in text')
        
    return conditions_search.group(0)





def read_pdf(pdf): 

# (?<=\nSURFACE WATER).*(?=\nREHABILITATION MANAGEMENT)
    try:
        doc = fitz.open(pdf)
    except Exception as e:
        logging.info(' ERROR: PDF: ' + pdf + ' could not open. Error was ' + str(e))
        return False, False    
    
    i = 1
    water_match = ''
    bookend1 = ""
    bookend2 = ""
    water_section_matched = False
    next_section_matched = False
    header_found = False

    for page in doc:  
        text = page.get_text()
          
        if header_found == False:           # skip CONTENTS page
            
            contents_match = regex.search("CONTENTS|INDEX", text) 

            if contents_match != None: 
                header_found = True
                print(f'PDF: {pdf} | Skipping Contents Page no: {i} | Match: {contents_match}')
                i = i + 1
                continue
        
        
        if water_section_matched == False:    # search for start of the "Water" Section
        
            for water_section in water_sections:
              
                water_pattern = regex.compile(r'(\n\b[\d\s]*[\.]*[\d\s]*)' + regex.escape(water_section) + r'(\b)') # Search which allows numeric before header
                water_search = water_pattern.search(text)

                if water_search != None:
                  
                    water_section_matched = True
                    print(f'{pdf} Found Water Sect: {water_section} on Page no: {i}')
                    logging.info(' Found Water Section: ' + water_section + ' on Page: ' + str(i))
                    bookend1 = water_section
                    start_page = i
                    break  

        
        
        if water_section_matched == True:       # found the start of the water section, now search for the start of the next section
          
            for next_section in next_sections:
              
                next_pattern = regex.compile(r'(\b[\d\s]*[\.]*[\d\s]*)' + regex.escape(next_section) + r'(\b)')
                next_search = next_pattern.search(text)

                if next_search != None:
                  
                    print(f'{pdf} Found Next Sect: {next_section} on Page no: {i}')
                    logging.info(' Found Next Section: ' + next_section + ' on Page: ' + str(i))
                    next_section_matched = True
                    bookend2 = next_section
                    end_page = i
                    if end_page <= start_page: # avoid finding next_section that is above the water_section!
                        continue
                    else:
                        break
                
                if next_section_matched == True:
                    break 
            
          
        i = i + 1

    if water_section_matched == False:
        logging.info(' PDF: ' + pdf + ' Skipping... Water Section not matched'  )
        result = False, False
    elif next_section_matched == False:
        logging.info(' PDF: ' + pdf + ' Skipping... Next Section not matched'  )
        result = False, False

    else:
        result = [start_page,end_page],[bookend1,bookend2]
    
    doc.close()
    return result





def read_pdfs(pdfs):
  
    for i in range(len(pdfs)):
        logging.info(' Started processing ' + pdfs.iloc[i,0] + ' at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        pages, bookends = read_pdf(pdfs.iloc[i,0])

        if pages != False: 
            alltext = consolidate_pages(pdfs.iloc[i,0],pages)
            write_ok = write_text(pdfs.iloc[i,0],alltext)
        else:
            logging.info(' ERROR PDF: ' + pdfs.iloc[i,0] + ' could not match Section(s) ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            continue

        searchtext = search_text(pdfs.iloc[i,0],alltext,bookends)

        if searchtext != False:
            write_ok = write_pages(pdfs.iloc[i,0],searchtext)

        logging.info(' Finished processing ' + pdfs.iloc[i,0] + ' at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
  
  


def get_pdf_paths(pdfs):
    
    pdf_ignore = pd.read_csv(csv_dir + 'pdf_ignore.csv')    # get files flagged to be discarded
    pdf_paths = []
    for i in range(len(pdfs)):

        ignore = False
        for j in range(len(pdf_ignore)):
            if os.path.basename(pdf_ignore.iloc[j,0]) == pdfs.iloc[i,11]:
                ignore = True
                break

        if ignore == False:        
            pdf_path = files_dir + pdfs.iloc[i,11]
            pdf_paths.append(pdf_path)
        else:
            logging.info(' Ignoring ' + files_dir + pdfs.iloc[i,11] + ' at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))     

    return pdf_paths




def read_all_pdfs():

    pdfs = pd.read_csv(csv_dir + 'train.csv')
    return pdfs




def main():

    setupLogging()
    pdfs = read_all_pdfs()
    pdf_paths = pd.DataFrame(get_pdf_paths(pdfs))
    read_pdfs(pdf_paths)
    logging.info(' Logging ended at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

if __name__ == "__main__":
    main()  


#def write_pages(pdf,pg):
#
#  print(pg)
#  fname = os.path.basename(pdf)
#  tname = text_dir + fname[:-3] + "txt"
#  doc = fitz.open(pdf)
#  text_filename = open(tname, "wt")
#
#  for i in range((pg[0] - 1), pg[1]):
#   
#    text = doc.get_page_text(i)
#    text_filename.write(text)
#
#  text_filename.close()
#  doc.close()  
#
#
#def read_pdf2(pdf):  # Option 2: extract as html and parse with bs4
#
#  doc = fitz.open(pdf)
#  htmlname = pdf[:-3] + "html"
#  print(htmlname)
#  
#  fname = open(htmlname, "wt")
#
#  for page in doc:  
#      for line in page.get_text("html").splitlines():  # get plain text (is in UTF-8)
#        fname.write(line)  # write text of page
##     out.write(bytes((12,)))  # write page delimiter (form feed 0x0C)
#  fname.close()
#
#
#
#
#def read_pdf3(pdf): 
#
## (?<=\nSURFACE WATER).*(?=\nREHABILITATION MANAGEMENT)
#
#  doc = fitz.open(pdf)
#  
#  i = 1
#  water_match = ''
#  water_section_matched = False
#  next_section_matched = False
#  header_found = False
#
#  for page in doc:  
#    text = page.get_text()
#      
#    if header_found == False:           # skip CONTENTS page
#        
#      contents_match = re.search("CONTENTS|INDEX", text) 
#       
#      if contents_match != None: 
#        header_found = True
#        print(f'PDF: {pdf} | Skipping Contents Page no: {i} | Match: {contents_match}')
#        i = i + 1
#        continue
#    
#    
#    if water_section_matched == False:    # search for start of the "Water" Section
#    
#      for water_section in water_sections:
#
#        water_pattern = re.compile(r'(\n\b[\d\s]*[\.]*[\d\s]*)' + re.escape(water_section) + r'(\b)') # Search which allows numeric before header
#        water_search = water_pattern.search(text)
#
#        if water_search != None:
#
#          water_section_matched = True
#          print(f'{pdf} Found Water Sect: {water_section} on Page no: {i}')
#          logging.info(' Found Water Section: ' + water_section + ' on Page: ' + str(i))
#          start_page = i
#          break  
#          
#   
#   
#    if water_section_matched == True:       # found the start of the water section, now search for the start of the next section
#      
#      for next_section in next_sections:
#
#        next_pattern = re.compile(r'(\n\b[\d\s]*[\.]*[\d\s]*)' + re.escape(next_section) + r'(\b)')
#        next_search = next_pattern.search(text)
#
#        if next_search != None:
#
#          print(f'{pdf} Found Next Sect: {next_section} on Page no: {i}')
#          logging.info(' Found Next Section: ' + next_section + ' on Page: ' + str(i))
#          next_section_matched = True
#          end_page = i
#          break
#
#        if next_section_matched == True:
#          break 
#
#      
#    i = i + 1
#
#  if water_section_matched == False:
#    logging.info(' ERROR Couldn\'t find Water Section in file ' + pdf )
#    result = False
#  else:
#    result = [start_page,end_page]
#  
#  doc.close()
#  return result
#

def read_pdf1(pdf): 

    allpages=""
    bookend1=""
    bookend2=""

    doc = fitz.open(pdf)
    logging.info(' PDF: ' + pdf + ' opened file and extracting all text')
    

    for page in doc:

        text = page.get_text("text")
        allpages = allpages + text
  
    write_ok = write_text(pdf,allpages,text_dir)
    

    water_search = None
    next_search = None
    for water_section in water_sections:
        water_pattern = regex.compile(r'(\n\b[\d\s]*[\.]*[\d\s]*)' + regex.escape(water_section) + r'(\b)') # Search which allows numeric before header
        water_search = water_pattern.search(allpages)    

        if water_search != None:
            print(water_search)
            logging.info(' PDF: ' + pdf + ', Found Water Section: ' + water_section + 'in text')
            bookend1 = water_section
            break
    
    
    if water_search != None:
        
        for next_section in next_sections:
            next_pattern = regex.compile(r'(\n\b[\d\s]*[\.]*[\d\s]*)' + regex.escape(next_section) + r'(\b)')
            next_search = next_pattern.search(allpages)

            if next_search != None:
                print(next_search)
                logging.info(' PDF: ' + pdf + ', Found Next Section: ' + next_section + 'in text')
                bookend2 = next_section
                break
    else:
        logging.info(' ERROR PDF: ' + pdf + ', Couldn\'t find Water Section ' + water_section + 'in text')
        return False

    #Extract text between bookends    
    # from regex101.com (?<=\nSURFACE WATER).*(?=\nREHABILITATION MANAGEMENT)
    # (?<=\nWATER).*(?=\nBIODIVERSITY)

    if bookend1 != "" and bookend2 != "":
        pattern = '(?<=\\n' +bookend1 + ').*(?=' + bookend2 + ')' 
#        pattern = '(?<=\\n' +bookend1 + ')[\d\s]*[\.]*[\d\s]*(?=\\n' + bookend2 + ')[\d\s]*[\.]*[\d\s]*'
        print(f"Pdf: {pdf}, Pattern: {pattern}")
        logging.info(' PDF: ' + pdf + ', Extracting text using search pattern ' + pattern + '')
        conditions_pattern = regex.compile(pattern, regex.DOTALL)    
        conditions_search = conditions_pattern.search(allpages)

        print(conditions_search)
        if (conditions_search == None):
            logging.info(' ERROR PDF: ' + pdf + ', Couldn\'t find pattern ' + pattern + ' in text')
            return False

        logging.info(' PDF: ' + pdf + ', search result' + str(conditions_search) + ' in text')
        doc.close()
        logging.info(' PDF: ' + pdf + ' closed file')
    
    return conditions_search.group(0)
