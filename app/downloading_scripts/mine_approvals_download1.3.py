# download_wrapper.py

# import pymysql
import pandas as pd
import numpy as np
import requests
import logging
import glob, os
import time
import datetime
import csv
#import sy
#import app.utils.flutils.py

from bs4 import BeautifulSoup
from datetime import date
# from flutils import get_all_urls

# from mine_approvals_download_1_3 import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
 

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--verbose')
chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "./downloads",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
})



url1 = 'https://www.planningportal.nsw.gov.au/major-projects/projects/search-name/list?name=&search_type=name&case_stage_name=Determination&development_type=11996&project_industry=All&case_type=All&determination_authority=All&decision=12556&local_council=All&determination_date_from=&determination_date_to=&current_display=name_list&projects-search-submit-form=&minx=130.18867187499947&maxx=163.41132812499063&miny=-40.392480174959964&maxy=-26.485205756207463&searchvalue=&page='
url2 = 'https://www.planningportal.nsw.gov.au/major-projects/projects/search-name/list?name=&search_type=name&case_stage_name=Determination&development_type=11996&project_industry=All&case_type=All&determination_authority=All&decision=12106&local_council=All&determination_date_from=&determination_date_to=&current_display=name_map&projects-search-submit-form=&minx=130.18867187499697&maxx=163.41132812498816&miny=-40.39248017495943&maxy=-26.485205756206827&searchvalue=&page='
workingdir = "/home/admin/dockers/masters/app/"
download_dir = "/home/admin/dockers/masters/data/downloads/"
logs_dir = "/home/admin/dockers/masters/data/downloads/logs/"

data = {'url' : [url1, url2],
        'pages' : [2,18]
}
df = pd.DataFrame(data, columns = ['url','pages'])


def setupLogging(dest_dir=None):

    if dest_dir is None:
        dest_dir = os.path.realpath("data/downloads/logs")
    
    logfile = dest_dir + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + ".log"
    logging.basicConfig(filename=logfile,level=logging.INFO)
    logging.info('-' * 80)
    logging.info(' Logging started at ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))




def remove_dups(dups_fname,dest_dir=None):

    if dest_dir is None:
        dest_dir = os.path.realpath("data/downloads/logs")

    dups_dest = os.path.join(dest_dir, dups_fname) 
    no_dups_dest = os.path.join(dest_dir, ('final_' + dups_fname))

    df1 = pd.read_csv(dups_dest, sep=",")
    df1.drop_duplicates(subset=['Download_File'], inplace=True)

    # Write the results to a different file
    df1.to_csv(no_dups_dest, index=False)




def file_writer(data,fname, dest_dir=None):

    logging.info('Writing CSV file ' + fname + ' ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    if dest_dir is None:
        dest_dir = os.path.realpath("data/downloads/logs")

    destination = os.path.join(dest_dir, fname) 
    
    if os.path.exists(destination):
        data.to_csv(destination,encoding='utf-8',index=False,mode='a',header=False)
    else:    
        data.to_csv(destination,encoding='utf-8',index=False,mode='a')   

    logging.info('Finished writing CSV ' + fname + ' ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    


def download_pdf(f_url, fname, dest_folder=None):

    logging.info('Downloading ' + f_url + ' ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))   
    if dest_folder is None:
        dest_folder = os.path.realpath("data/downloads")
    
    filename = fname.replace('/','') + '.pdf'
    destination = os.path.join(dest_folder, filename)

    try:
        fname = requests.get(f_url)
        if os.path.exists(destination) == False:
            open(destination, 'wb').write(fname.content)

        logging.info('Finished writing ' + destination + ' ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        return filename    
    except:
        logging.info('File ' + destination + ' already exists. Download failed ' + f_url + ' ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        return "download_failed" 


def get_download_link(f_url):

    logging.info('Scrapeing started for Download URL ' + f_url + ' ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    p_url = ''
    reqs = requests.get(f_url)
    time.sleep(3)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('a'):
        
        p_name = str(link.string)
        if p_name.find('Consolidated') != -1:
            p_url = str(link.get('href'))
            print(p_url)
        elif p_name.find('consolidated') != -1:
            p_url = str(link.get('href'))    
            print(p_url)
        elif p_name.find('- Consolida') != -1:
            p_url = str(link.get('href'))    
            print(p_url)        
        elif p_name.find('Consent') != -1:
            p_url = str(link.get('href'))    
            print(p_url)

    logging.info('Scrapeing finished for Download URL ' + p_url + ' ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    return p_url



def get_project_data(url):
    
    logging.info('Scrapeing started for Project URL ' + url + ' ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    download_link = ""
    driver = webdriver.Chrome(options=chrome_options)    # change the <path_to_place_downloaded_file> to your directory where you would like to place the downloaded file
    driver.get(url)

    try:
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "project__details")))
    finally:
        element = driver.find_elements_by_class_name ("project__details")

    project_detail = []
    for i in range(len(element)):
    
        project_detail = (element[0].text).splitlines() 
    
    driver.quit()
    logging.info('Scrapeing finished for Project URL ' + url + ' ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    return project_detail 


def already_downloaded(fname, dest_folder=None):

    if dest_folder is None:
        dest_folder = os.path.realpath("data/downloads")
    
    filename = fname.replace('/','') + '.pdf'
    destination = os.path.join(dest_folder, filename)

    if os.path.exists(destination == True):
        logging.info(destination + ' already exists. Skipping .. ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))   
        return True
    else:
        return False


def get_page_links(url):

    logging.info('Scrapeing started for Page URL ' + url + ' ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    reqs = requests.get(url)
    # time.sleep(3)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    # time.sleep(3)
    urls = []
    for link in soup.find_all('a'):

        p_url = str(link.get('href'))
        p_name = str(link.string)

        if (already_downloaded(p_name)) == True:
            pass

        elif p_url[0:24] == "/major-projects/project/":
            project_link = "https://www.planningportal.nsw.gov.au" + p_url

            project_detail = get_project_data(project_link)
            download_link = get_download_link(project_link)
            consent_download = download_pdf(download_link,project_detail[2])
            if consent_download == "download_failed":
                pass
            else:
                urls.append([datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),project_detail[2], p_name, project_detail[4],
                        project_detail[6],project_detail[8],project_detail[10],
                        project_detail[12],project_detail[14],project_link,download_link,consent_download])
   
    dff = pd.DataFrame(urls,columns=['Downloaded','Application_No','Project_Name','Assessment_Type','Development_Type', \
                                    'LGA','Decision','Determination_Date','Decider','URL','Download_URL','Download_File']) 

    file_writer(dff,'consent_downloads.csv')
    logging.info('Scrapeing finished for Page URL ' + url + ' ' + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))



def get_search_urls(urls):                          # iterate thru the urls search list

    for i in range(len(urls)):                       

        url_string = str(urls.iloc[i,0])
        for j in range(urls.iloc[i,1]):              # create search url with page number
            url = url_string + str(j)
            search_urls = get_page_links(url)            
    
    return search_urls



def scrape_all_webdata():

    success = get_search_urls(df)
    remove_dups('consent_downloads.csv')
        

def main():

    setupLogging()
    scrape_all_webdata()
    


if __name__ == "__main__":
    main()