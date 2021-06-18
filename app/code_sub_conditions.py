#code_sub_conditions.py

import pandas as pd
import numpy as np
import requests
import regex,re
import logging
import glob, os, sys, inspect
from datetime import datetime, date
from contextlib import suppress



workingdir = "/home/admin/dockers/masters/app/"
csv_dir = "/home/admin/dockers/masters/data/csv/"
logs_dir = "/home/admin/dockers/masters/data/code_consents/logs/"
cond_dir = "/home/admin/dockers/masters/data/cond_cat/"
consents_dir = "/home/admin/dockers/masters/data/code_consents/"


def setupLogging(dest_dir=None):

    if dest_dir is None:
        dest_dir = os.path.realpath(logs_dir)
    
    logfile = logs_dir + str(datetime.now().strftime('%Y%m%d%H%M%S')) + ".log"
    logging.basicConfig(filename=logfile,level=logging.INFO)
    logging.info('-' * 80)
    logging.info(inspect.stack()[0][3] + ' Logging started at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))



def write_csv(df_scored):
    
    cat1 = []
    cat2 = [] 
    cat3 = [] 
    cat4 = []
    
    
    fname1 = consents_dir + 'cat1/coded_sub_section.csv'
    fname2 = consents_dir + 'cat2/coded_sub_section.csv'
    fname3 = consents_dir + 'cat3/coded_sub_section.csv'
    fname4 = consents_dir + 'cat4/coded_sub_section.csv'
    fname5 = consents_dir + 'coded_sub_section.csv'
    
    
    pd.set_option('display.max_rows', None)

    for i in range(len(df_scored)):

        fields = [df_scored.iloc[i,0],df_scored.iloc[i,1],df_scored.iloc[i,2],df_scored.iloc[i,3],df_scored.iloc[i,4],df_scored.iloc[i,5]]
           
        if df_scored.iloc[i,4] == 1:
            cat1.append(fields)
        elif df_scored.iloc[i,4] == 2:
            cat2.append(fields)
        elif df_scored.iloc[i,4] == 3:
            cat3.append(fields)
        elif df_scored.iloc[i,4] == 4:
            cat4.append(fields)
        else:
            pass            
    

    df1 = pd.DataFrame(cat1,columns=['Textfile','Determination_Year','Sub_Header','Sub_Section','Cond_Category','EScore'])
    df1.to_csv(fname1,encoding='utf-8',index=False,mode='w') 
    logging.info(inspect.stack()[0][3] + ' write_csv CSV: ' + fname1)
    
    df2 = pd.DataFrame(cat2,columns=['Textfile','Determination_Year','Sub_Header','Sub_Section','Cond_Category','EScore'])
    df2.to_csv(fname2,encoding='utf-8',index=False,mode='w') 
    logging.info(inspect.stack()[0][3] + ' write_csv CSV: ' + fname2)
    
    df3 = pd.DataFrame(cat3,columns=['Textfile','Determination_Year','Sub_Header','Sub_Section','Cond_Category','EScore'])
    df3.to_csv(fname3,encoding='utf-8',index=False,mode='w') 
    logging.info(inspect.stack()[0][3] + ' write_csv CSV: ' + fname3)
    
    df4 = pd.DataFrame(cat4,columns=['Textfile','Determination_Year','Sub_Header','Sub_Section','Cond_Category','EScore'])
    df4.to_csv(fname4,encoding='utf-8',index=False,mode='w') 
    logging.info(inspect.stack()[0][3] + ' write_csv CSV: ' + fname4 )
    
    
    df_scored.to_csv(fname5,encoding='utf-8',index=False,mode='w') 
    logging.info(inspect.stack()[0][3] + ' write_csv CSV: ' + fname5 )

    return True  # need to check status of file     


def get_sub_cond_year(df_year,textfile):
    
    application_no = os.path.basename(textfile)
    try:
        df_yr = df_year.loc[df_year['Application_No'] == application_no[:-4],['Determination_Year']]
        logging.info(inspect.stack()[0][3] + ' Found year ' + str(df_yr.iloc[0,0]) + ' for application ' + application_no)

#        print(f"Year: {df_yr.iloc[0,0]} application_no: {application_no}")
        result = str(df_yr.iloc[0,0])
    except Exception as e:
        logging.info(inspect.stack()[0][3] + ' ERROR: TEXT: ' + textfile + ' could not find ' + application_no + '. Error was ' + str(e))
        result = None
    return result


    

def score_consent_cond(df_text,df_es):
    
    df_cond1 = pd.DataFrame(columns=['Textfile','Determination_Year','Sub_Header','Sub_Section','Cond_Category','EScore'])
    df_cond = pd.DataFrame(columns=['Textfile','Determination_Year','Sub_Header','Sub_Section','Cond_Category','EScore'])
    df_text['Sub_Section'] = df_text['Sub_Section'].str.replace('\,', '') # remove commas in conditions text

    df_year = get_year()
    

    for i in range(len(df_text)):                           # loop thru the consent by category csv files
        
                                                             # Grab the first sentence
        conditions = []
        prev_rule = 0
        es = 0
        yr = get_sub_cond_year(df_year,df_text.iloc[i,0])

        for j in range(len(df_es)):                         # loop through the enforceable word dict csv file and extract ew_list

            ew_list = df_es.iloc[j,2].split(",")            # loop through the ew_list of similar terms
            for ew in ew_list:

                ew = ew.replace("\'","")                    # strip the quotes from the list members

                if str(df_text.iloc[i,3]).find(ew) == -1:   

                    pass                                    # pass if an enforceable word from the list is not found in the text

                else:                                       # calc the enforceable word score
                    if es == 0:
                        es = df_es.iloc[j,3]
                    else:
                        es = es * df_es.iloc[j,3]          # multiply es  
#                        if es >= df_es.iloc[j,3]:         # use the lowest enforceable word score
#                            es = df_es.iloc[j,3]          # (hashed out)
                    
                    logging.info(inspect.stack()[0][3] + ' Scoring ' + os.path.basename(df_text.iloc[i,0] + ' ') 
                            + str(df_text.iloc[i,1]) + ' Sub_Sect ' 
                            + str(df_text.iloc[i,2]) + ' Category '
                            + str(df_es.iloc[j,1]) + ' ('
                            + str(df_es.iloc[j,3]) + ') '
                            + str(ew)  + ' '
                            + str(es)
                            )
                    break                                   # only score 1 word from each enforceable word list

        else: # Append at the end of the for.. else loop


            fields = [df_text.iloc[i,0],yr,df_text.iloc[i,1],df_text.iloc[i,3],df_text.iloc[i,2],es]
            conditions.append(fields)    

        df_cond1 = pd.DataFrame(conditions,columns=['Textfile','Determination_Year','Sub_Header','Sub_Section','Cond_Category','EScore'])
        df_cond  = df_cond.append(df_cond1)
    
    return df_cond


def read_consent_file(textfile):

    logging.info(inspect.stack()[0][3] + ' Reading in ' + textfile + ' ')
    df_text = pd.read_csv(textfile,header=0)
    return df_text
    



def code_consent_files(consent_files,df_es):

    df = pd.DataFrame(columns=['Textfile','Determination_Year','Sub_Header','Sub_Section','Cond_Category','EScore'])

    for consent_file in consent_files:

        df_consent_text = read_consent_file(consent_file)
        df_score_text = score_consent_cond(df_consent_text,df_es)
        df = df.append(df_score_text)

    write_ok = write_csv(df)
    return write_ok


def get_year():
    logging.info(inspect.stack()[0][3] + ' Reading in ' + csv_dir + 'train.csv')
    df_year = pd.read_csv(csv_dir + 'train.csv',usecols=[2,3,1],header=0)
    
    return df_year


def get_consent_files():
    
    fname1 = cond_dir + 'cat1/consent_sub_section.csv'
    fname2 = cond_dir + 'cat2/consent_sub_section.csv'
    fname3 = cond_dir + 'cat3/consent_sub_section.csv'
    fname4 = cond_dir + 'cat4/consent_sub_section.csv'
    consent_files = []
    
    for i in range(1,5):
        fname = 'fname' + str(i)
        consent_files.append(eval(fname))

    return consent_files



def get_sub_headers():
    logging.info(inspect.stack()[0][3] + ' Reading in ' + csv_dir + 'derived_enforceability_score1.2csv')
    df_es = pd.read_csv(csv_dir + 'derived_enforceability_score1.2.csv',header=0)
    return df_es


def main():

    consent_files = []
    setupLogging()
    df_es = get_sub_headers()

    
    consent_files = get_consent_files()
    code_success = code_consent_files(consent_files,df_es)
    print(code_success)

    logging.info(inspect.stack()[0][3] + ' Logging ended at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

if __name__ == "__main__":
    main()  

