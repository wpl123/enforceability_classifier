import pandas as pd
import numpy as np
import requests
import regex,re
import logging
import glob, os, sys, inspect
from datetime import datetime, date



workingdir = "/home/admin/dockers/masters/app/"
csv_dir = "/home/admin/dockers/masters/data/csv/"
logs_dir = "/home/admin/dockers/masters/data/cond_cat/logs/"
files_dir = "/home/admin/dockers/masters/data/pdfminer/search/"
search_dir = "/home/admin/dockers/masters/data/cond_cat/search/"
cond_dir = "/home/admin/dockers/masters/data/cond_cat/cat"

def setupLogging(dest_dir=None):

    if dest_dir is None:
        dest_dir = os.path.realpath(logs_dir)
    
    logfile = logs_dir + str(datetime.now().strftime('%Y%m%d%H%M%S')) + ".log"
    logging.basicConfig(filename=logfile,level=logging.INFO)
    logging.info('-' * 80)
    logging.info(inspect.stack()[0][3] + ' Logging started at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))



def write_csv(conditions):
    
    for condition in conditions:
        pass
    #    print(condition)
    
    # fname = cond_dir + cond_category + '/consent_sub_section.csv'
    # fields = []
    # 
    # df = pd.DataFrame(fields,columns=['Application_No','Sub_Header','Cond_Category','sub_section'])
    # df.to_csv(fname,encoding='utf-8',index=False,mode='a') 
    # logging.info(' CSV: ' + fname + ' written to')
    return True  # need to check status of file     




def search_text(bookends,text):  # conditions = [textfile, bookend1, bookend2]

    conditions = []
    for args in bookends:

        textfile = str(args[0])
        bookend1 = str(args[1])
        bookend2 = str(args[2])

        if bookend1 != "" and bookend2 != "":

            pattern = '(?<=' + bookend1 + ').*(?=' + bookend2 + ')'

            logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' Extracting text using search pattern ' + pattern + '')

            sub_header_pattern = regex.compile(pattern,regex.DOTALL)    
            sub_header_search = sub_header_pattern.search(text)


            if (sub_header_search == None):
                logging.info(inspect.stack()[0][3] + ' ERROR TEXT: ' + textfile + ' Couldn\'t find pattern ' + pattern + ' in text')
                return False
            else:
                logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' search result is ' + str(sub_header_search)[0:80] + ' in text')
                search_result = str(sub_header_search.group(0))

            fields = [textfile,bookend1,search_result]
            conditions.append(fields)
        else:
            logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' missing bookends in search string' + str(sub_header_search) + ' in text')
            result = False      
    if conditions != []:
        result = conditions
    return result



def search_line(textfile,sub_header,line,matchno,i):  # Note! no point matching for line feeds prior to this line

    #pattern = r'(\b)' + sub_header + r'(\b)'
    
    pattern = r'(\b)' + sub_header + r'(\s*\n)'
#    pattern = regex.compile(pattern,regex.DOTALL) 
#    search = pattern.search(line)
    search = regex.search(pattern,line,regex.DOTALL)

#    if i == 6 or i == 12:
#        print(f'Line: {i} pattern: {pattern}, line text: {line}')
    if search != None:
        section_matched = True
        logging.info(inspect.stack()[0][3] + '   TEXT: ' + os.path.basename(textfile) + ' Found ' + matchno + ' sub header: ' + str(pattern) + ' on line: ' + str(i))
        print(textfile, " matched ", search)
        return True  
    else:
#        logging.info(inspect.stack()[0][3] + '   TEXT: ' + os.path.basename(textfile) + matchno + ' Pattern ' + str(pattern) + ' not found on line: ' + str(i))
        return False




def get_bookends(textfile): 
    
    result = []
    bookends = []
    bookend1 = ""
    bookend2 = ""
    first_sub_header_matched = False
    second_sub_header_matched = False
    end_of_file = False
    previous_sub_header = ""
    # Sub_Headers = df_sub['Sub_Header'].unique()   # need category too
    df_sub = get_sub_headers()    
    i = 0
    found_sub_headers = []

    try:
        doc = open(textfile,'r') #,encoding='utf8'
#            text = doc.read()
        
        
        for line in doc:   # Read each line in the text document 
            i = i + 1
    
            # re-use bookend2 for bookend1 on the next iteration
            if (bookend2 != "") & (bookend1 != bookend2):
                bookend1 = bookend2
                logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' Convert bookend2 ' + bookend2 + ' to bookend1 ')
                first_sub_header_matched = True
            
            if first_sub_header_matched == False:

            # Loop through the sub heading and check for first sub_header in the current line 
                for j in range(len(df_sub)):
                    # Skip already matched sub headers    
                    if df_sub.iloc[j,0] != '':    
                        sub_header = df_sub.iloc[j,0]
                    else:
                        continue    
                    
                    #Check for sub_header        
                    if search_line(textfile,sub_header,line,"first",i) == True:
                        first_sub_header_matched = True
                        bookend1 = sub_header
                        start_line = i  
                        logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' First sub header matched! ' + sub_header + ' ..deleting')
                        #remove the sub_header so it wont get matched as the first sub header again
                        df_sub.iloc[j,0] = '' 
    
                        break

###         Got a match on the first sub header now read down the file to the next subheader

            if first_sub_header_matched == True:
                # Loop through the sub heading and check for second sub_header in the current line 
                for j in range(len(df_sub)):
                
                    # Skip already matched sub headers
                    if df_sub.iloc[j,0] != '':    
                        sub_header = df_sub.iloc[j,0]
                    else:
                        continue   
                    
                    #Check for second sub_header        
                    if search_line(textfile,sub_header,line,"second",i) == True:
#                        print(f"post search second sub_header {sub_header}")
                        logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' Second sub header matched! ' + sub_header + ' ')
                        second_sub_header_matched = True
                        bookend2 = sub_header
                        end_line = i
                        #remove the sub_header so it wont get matched as the first sub header again
                        df_sub.iloc[j,0] = '' 
                        break  

            #Accumulate conditions for this text document            
            if second_sub_header_matched == True:
                fields = [textfile, bookend1, bookend2]
                bookends.append(fields)
                first_sub_header_matched = False
                second_sub_header_matched = False

        else: #End of for loop and reached EOF. Set bookend2 to the EOF i.e. \Z
            
            logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' Second sub header not matched! Matching EOF ')
            second_sub_header_matched = True
            bookend2 = "\Z"
            end_line = i
            fields = [textfile, bookend1, bookend2]
            bookends.append(fields)

        doc.close()
    except Exception as e:
        logging.info(inspect.stack()[0][3] + ' ERROR: TEXT: ' + textfile + ' could not open. Error was ' + str(e))
        return False, False

    if first_sub_header_matched == False:
        logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' Skipping... First sub header not matched'  )
        result = False, False
    elif second_sub_header_matched == False:
        logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' Skipping... Second sub header not matched'  )
        result = False, False
    else:
        try:
            doc = open(textfile,'r') #,encoding='utf8'
            text = doc.read()
            doc.close()

        except Exception as e:
            logging.info(inspect.stack()[0][3] + ' ERROR: TEXT: ' + textfile + ' could not open. Error was ' + str(e))
        
        if bookends != '':
            result = bookends,text
        else:
            result = False, False
        
    #    result = bookends,text
    
    return result





def get_conditions(textfiles):

    #1. extract and categorise conditions
    conditions = []
    for i in range(len(textfiles)):

        logging.info(inspect.stack()[0][3] + ' Started processing ' + os.path.basename(textfiles[i]) + ' at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        
        bookends,text = get_bookends(str(textfiles[i]))
        if bookends == False: 
            logging.info(inspect.stack()[0][3] + ' ERROR TEXT: ' + textfiles[i] + ' conditions error ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            continue
        elif text == False: 
            logging.info(inspect.stack()[0][3] + ' ERROR TEXT: ' + textfiles[i] + ' text error ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            continue    
        else:
            searchtexts = search_text(bookends,text)     # bookends = [textfile, bookend1, bookend2]
                                                        # searchtexts = [textfile,bookend1,search_result]
        
        
        if searchtexts != False:

            for searchtext in searchtexts:

                fields =[searchtext[0],searchtext[1],searchtext[2]]
                conditions.append(fields)

        logging.info(inspect.stack()[0][3] + ' Finished processing ' + textfiles[i] + ' at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
  

    return conditions



def get_sub_headers():
    df_sub = pd.read_csv(csv_dir + 'dict_cat_sub_headers.csv')

    return df_sub  


def get_categories():
    df_cat = pd.read_csv(csv_dir + 'consent_ewords.csv')
    
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
            logging.info(inspect.stack()[0][3] + ' Ignoring ' + files_dir + df_text.iloc[i,11] + ' at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))     

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
    
    
    conditions = get_conditions(textfile_paths) #TODO
    #conditions = get_conditions(["/home/admin/dockers/masters/data/pdfminer/search/MP06_0021-Mod-3.txt"])
    
    write_ok = write_csv(conditions)
    
    #textfile_paths = pd.DataFrame(get_textfile_paths(textfiles))
    logging.info(inspect.stack()[0][3] + ' Logging ended at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

if __name__ == "__main__":
    main()  



## defunct


