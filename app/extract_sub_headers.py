import pandas as pd
import numpy as np
import requests
import regex, re
import logging
import glob, os, sys
from datetime import datetime, date



workingdir = "/home/admin/dockers/masters/app/"
csv_dir = "/home/admin/dockers/masters/data/csv/"
logs_dir = "/home/admin/dockers/masters/data/cond_cat/logs/"
files_dir = "/home/admin/dockers/masters/data/pdfminer/search/"
search_dir = "/home/admin/dockers/masters/data/cond_cat/search/"



def setupLogging(dest_dir=None):

    if dest_dir is None:
        dest_dir = os.path.realpath(logs_dir)
    
    logfile = logs_dir + str(datetime.now().strftime('%Y%m%d%H%M%S')) + ".log"
    logging.basicConfig(filename=logfile,level=logging.INFO)
    logging.info('-' * 80)
    logging.info(' Logging started at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))



def write_text(textfile,all_text):
    fname = os.path.basename(textfile)
    tname = files_dir + fname[:-3] + "txt"

    text_filename = open(tname, "wt")
    text_filename.write(all_text)

    text_filename.close()
    logging.info(' TEXT: ' + tname + ' created')
    return True  # need to check status of file      



def write_csv(all_sub_headers):
    
    fname = csv_dir + 'consent_sub_headers.csv'
   
    unique_sub_headers = []
    unique_sub_headers = list(set(all_sub_headers))

    df = pd.DataFrame(unique_sub_headers,columns=['Sub_Header'])
    df.to_csv(fname,encoding='utf-8',index=False,mode='a') 
    logging.info(' CSV: ' + fname + ' created')
    return True  # need to check status of file     



def read_textfile(df_cat,textfile): 

    try:
        doc = open(textfile,'r') #,encoding='utf8'
        text = doc.read()
        doc.close()
    except Exception as e:
        logging.info(' ERROR: textfile: ' + textfile + ' could not open. Error was ' + str(e))
        return False
    
    i = 1
#    Sub_Headers = df_cat['Sub_Header'].unique()
    found_sub_headers = []
    search_headers = regex.findall(r'\n\s?\n[A-Z][A-Za-z\s]*\n',text)
    if search_headers != None:
    
        for found_sub_header in search_headers:
            stripped_sub_header = found_sub_header.replace('\n','')
            
            found_sub_headers.append(stripped_sub_header)

        return found_sub_headers       
    else:
        return False





def get_conditions(df_cat,textfiles):

    #1. extract and categorise conditions
    all_sub_headers = []
    for i in range(len(textfiles)):

        logging.info(' Started processing ' + textfiles[i] + ' at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        result = read_textfile(df_cat, textfiles[i])
        if result != False:

            for sub_header in result:
                all_sub_headers.append(sub_header)
        
        
        logging.info(' Finished processing ' + textfiles[i] + ' at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
  
    return all_sub_headers
  


def get_categories():
    df_cat = pd.read_csv(csv_dir + 'consent_ewords.csv')
#    df_cat = pd.DataFrame(categories)
    # extract Sub_header and Cond_Category as a df and remove duplicates
    
    return df_cat



def get_textfile_paths(df_text):
    
    textfile_ignore = pd.read_csv(csv_dir + 'textfile_ignore.csv')    # get files flagged to be discarded
    textfile_paths = []

    for i in range(len(df_text)):
        
        ignore = False
        for j in range(len(textfile_ignore)):
#            print(textfile_ignore.iloc[j,0],(files_dir + textfile))
            if os.path.basename(textfile_ignore.iloc[j,0]) == df_text.iloc[i,11]:
                ignore = True
                break

        if ignore == False:   
                
            textfile_path = files_dir + df_text.iloc[i,11][:-3] + "txt"
            textfile_paths.append(textfile_path)
        else:
            logging.info(' Ignoring ' + files_dir + df_text.iloc[i,11] + ' at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))     

    return textfile_paths


def get_textfiles():
    
#    textfiles = glob.glob(files_dir + '*')
    df_text = pd.read_csv(csv_dir + 'test.csv')
    textfile_paths = get_textfile_paths(df_text)
    return df_text, textfile_paths




def main():

    setupLogging()
    df_test, textfile_paths = get_textfiles()
    df_cat = get_categories()
    
    sub_headers = get_conditions(df_cat,textfile_paths)
    #sub_headers = get_conditions(df_cat,["/home/admin/dockers/masters/data/pdfminer/search/MP11_0047.txt"])
    result = write_csv(sub_headers)
    logging.info(' Logging ended at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

if __name__ == "__main__":
    main()  



## defunct


