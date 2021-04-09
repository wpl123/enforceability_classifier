import pandas as pd
import numpy as np
import os
from datetime import datetime, date
#from datetime import date

mydateparser = lambda x: datetime.strptime(x, "%d/%m/%Y")

df = pd.read_csv(
  'data/downloads/logs/consent_downloads1.csv',  #lambda x: datetime.strptime(x, '%d/%m/%Y'
  parse_dates=[7], date_parser=mydateparser,
  index_col="Determination_Date",
  keep_date_col=True
  
    
)

df.shape
df.dtypes

pd.set_option('display.max_rows', None)
dfs = df.loc['2012-01-01':]
dfs.sort_index(inplace=True)


year1 = 2012
i = 0
df1 = []
df2 = []

dest_dir = os.path.realpath("data/downloads/logs")
train_dest = os.path.join(dest_dir, 'train.csv')
test_dest = os.path.join(dest_dir, 'test.csv')

for index, row in dfs.iterrows():
    
    if (index.year == year1):
        print('train', index, index.year, dfs.iloc[i,1],dfs.iloc[i,2], dfs.iloc[i,3], dfs.iloc[i,4], dfs.iloc[i,5], dfs.iloc[i,6], dfs.iloc[i,7], dfs.iloc[i,8], dfs.iloc[i,9], dfs.iloc[i,10])
        train_fields = [index, index.year, dfs.iloc[i,1],dfs.iloc[i,2], dfs.iloc[i,3], dfs.iloc[i,4], dfs.iloc[i,5], dfs.iloc[i,6], dfs.iloc[i,7], dfs.iloc[i,8], dfs.iloc[i,9], dfs.iloc[i,10]]
        df1.append(train_fields)
        year1 = year1 + 1
    else:
        print('test', index, index.year, dfs.iloc[i,1],dfs.iloc[i,2], dfs.iloc[i,3], dfs.iloc[i,4], dfs.iloc[i,5], dfs.iloc[i,6], dfs.iloc[i,7], dfs.iloc[i,8], dfs.iloc[i,9], dfs.iloc[i,10])
        test_fields = [index, index.year, dfs.iloc[i,1],dfs.iloc[i,2], dfs.iloc[i,3], dfs.iloc[i,4], dfs.iloc[i,5], dfs.iloc[i,6], dfs.iloc[i,7], dfs.iloc[i,8], dfs.iloc[i,9], dfs.iloc[i,10]]
        df2.append(test_fields)
    
    i = i + 1

df_train = pd.DataFrame(df1,columns=['Determination_Date','Determination_Year','Application_No','Project_Name','Assessment_Type','Development_Type', \
                                'LGA','Decision','Decider','URL','Download_URL','Download_File']) 
df_test = pd.DataFrame(df2,columns=['Determination_Date','Determination_Year','Application_No','Project_Name','Assessment_Type','Development_Type', \
                                'LGA','Decision','Decider','URL','Download_URL','Download_File'])

df_train.to_csv(train_dest,encoding='utf-8',index=False,mode='a') 
df_test.to_csv(test_dest,encoding='utf-8',index=False,mode='a')                                                                          