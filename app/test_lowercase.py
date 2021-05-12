# import regex
# 
# text = '" co-ordinate modelling programs for validation, structures over time.'
# 
# pattern = "\A\s*[a-z]"
# if regex.search(pattern,text) != None:
#     print(text)    
#     text = ''

import pandas as pd


text = 'The Proponent shall ensure that all surface water discharges from the site comply with the discharge limits both volume and quality set for the project in any EPL.'
print(f"Text: {text}")

csv_dir = "/home/admin/dockers/masters/data/csv/"


def highlight_words(sentence, words):
    for i in range(len(sentence)):
        for j in range(len(words)):    
            if sentence.lower().startswith(words[j].lower(), i):
                sentence = sentence[:i] + sentence[i:i+len(words[j])].upper() + sentence[i+len(words[j]):]
    return sentence




def get_es():

    df_es = pd.read_csv(csv_dir + 'derived_enforceability_score1.2.csv',header=0)
    return df_es


def get_words(df_es):

    words = []
    for i in range(len(df_es)):

        ew_list = df_es.iloc[i,2].split(",")

        for ew in ew_list:
            ew = ew.replace("\'","")   
            words.append(ew)

    return words


def main():

    df_es = get_es()

    words = get_words(df_es)
    print(highlight_words(text,words))

if __name__ == "__main__":
    main()  
