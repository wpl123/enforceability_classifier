import pandas as pd

textfile = '/home/admin/dockers/masters/data/csv/dict_sub_headers_edit.csv'

df_cat = pd.read_csv(textfile)
df_cat = df_cat['Sub_Header'].str.strip()

df_cat = df_cat.drop_duplicates()

print(df_cat)

fname = '/home/admin/dockers/masters/data/csv/dict_sub_headers.csv'

df_cat.to_csv(fname,encoding='utf-8',index=False,mode='a') 