import pandas as pd
import numpy as np
import os, csv
#import datetime
from datetime import datetime, date



df = pd.read_csv('data/csv/sample_set_category_data.csv')
df['Enforceable Words'] = df['Enforceable Words'].astype(str)
df['Contextual Words'] = df['Contextual Words'].astype(str)
df['Year'] = df['Year'].astype(int)

dest_dir = os.path.realpath("data/csv/")
destination = os.path.join(dest_dir, 'consent_ewords.csv')
destination2 = os.path.join(dest_dir, 'dict_ewords.csv')
destination3 = os.path.join(dest_dir, 'dict_cwords.csv')

ewords=()
consent_ewords=[]
for i in range(len(df)):
    
    ewords = list(df.iloc[i,7].split(','))
   
    for j in range(len(ewords)):
        consent_ewords.append([datetime.now().strftime('%d/%m/%Y %H:%M:%S'),df.iloc[i,0], df.iloc[i,1], df.iloc[i,2],
                df.iloc[i,3], df.iloc[i,4], df.iloc[i,5], df.iloc[i,6], ewords[j], df.iloc[i,8]])
    
    
consent_data = pd.DataFrame(consent_ewords,columns=['Created','Approval_Name','Year','Header','Sub_Header','Section', \
                                   'Para','Cond_Category','Enforceable_Words','Contextual_Words'])
consent_data.sort_values(by=['Year','Approval_Name'],inplace=True, ascending=[True,True])                                    
consent_data.to_csv(destination,encoding='utf-8',index=False,mode='w')

dict_ewords = consent_data.Enforceable_Words.unique()

dict_data = pd.DataFrame(dict_ewords,columns=['Enforceable_Words'])
dict_data.sort_values(by=['Enforceable_Words'],inplace=True, ascending=[True])
dict_data.to_csv(destination2,encoding='utf-8',index=False,mode='w') 

dict_cwords = consent_data.Contextual_Words.unique()

dict_data2 = pd.DataFrame(dict_cwords,columns=['Contextual_Words'])
dict_data2.sort_values(by=['Contextual_Words'],inplace=True, ascending=[True])
dict_data2.to_csv(destination3,encoding='utf-8',index=False,mode='w')