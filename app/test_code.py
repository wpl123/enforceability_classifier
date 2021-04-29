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

def score_consent_cond(df_text,df_es):
    
#    print('score_consent_cond: ', df_text)
    df_cond1 = pd.DataFrame(columns=['Textfile','Sub_Header','Sub_Section','Cond_Category','EScore'])
    df_cond = pd.DataFrame(columns=['Textfile','Sub_Header','Sub_Section','Cond_Category','EScore'])
    df_text['Sub_Section'] = df_text['Sub_Section'].str.replace('\,', '') # remove commas in conditions text
    
#    print(f"score_consent_cond {df_text}")
    for i in range(len(df_text)):                           # loop thru the consent by category csv files
        
#        print("i: ", i)    
        conditions = []
        prev_rule = 0
        es = 0
        for j in range(len(df_es)):                         # loop through the enforceable word dict csv file and extract ew_list
              
            ew_list = df_es.iloc[j,2].split(",")
#            print(f"j: {j} {ew_list}")  
                        # loop through the ew_list
            for ew in ew_list:
                    
#                print(f"ew: {ew}")    
                ew = ew.replace("\'","")                    # strip the quotes from the list members

                if str(df_text.iloc[i,2]).find(ew) == -1:   # break if an enforceable word is not found in the text
#                    print(f"Pass Sub_Header {df_text.iloc[i,1]} EWord {ew} ({df_es.iloc[j,3]}) Score {es} ")
                    pass

                else:   
                                                                         # calc the enforceable word score
                    if es == 0:
                        es = df_es.iloc[j,3]
                        print(f"Sub_Header {df_text.iloc[i,1]} EWord {ew} ({df_es.iloc[j,3]}) Score {es} ") 
                    else:
                        es = es * df_es.iloc[j,3]
                        print(f"Sub_Header {df_text.iloc[i,1]} EWord {ew} ({df_es.iloc[j,3]}) Score {es} ")  
        
        else: # Append at the end of the for.. else loop


            fields = [df_text.iloc[i,0],df_text.iloc[i,1],df_text.iloc[i,2],"2",es]
            conditions.append(fields)    

        df_cond1 = pd.DataFrame(conditions,columns=['Textfile','Sub_Header','Sub_Section','Cond_Category','EScore'])
        df_cond  = df_cond.append(df_cond1)
    
    return df_cond


def read_consent_file(textfile):

    df_text = pd.read_csv(textfile,header=0)
#    print("read_consent_file: ", df_text)
    return df_text

def get_sub_headers():
    df_es = pd.read_csv(csv_dir + 'derived_enforceability_score1.2.csv',header=0)
#    print("read_sub_headers", df_es)
    return df_es    

def main():

    textfile = '/home/admin/dockers/masters/data/cond_cat/test_code.csv'
    fname = '/home/admin/dockers/masters/data/cond_cat/test_code.txt'
    df_es = get_sub_headers()

    
    df_text = read_consent_file(textfile)
    df_coded = score_consent_cond(df_text,df_es)

    df_coded.to_csv(fname,encoding='utf-8',index=False,mode='w') 
    

if __name__ == "__main__":
    main()  

