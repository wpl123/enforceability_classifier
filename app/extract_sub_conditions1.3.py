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
cond_dir = "/home/admin/dockers/masters/data/cond_cat/"

def setupLogging(dest_dir=None):

    if dest_dir is None:
        dest_dir = os.path.realpath(logs_dir)
    
    logfile = logs_dir + str(datetime.now().strftime('%Y%m%d%H%M%S')) + ".log"
    logging.basicConfig(filename=logfile,level=logging.INFO)
    logging.info('-' * 80)
    logging.info(inspect.stack()[0][3] + ' extract_sub_conditions1.2.py Logging started at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))



def write_csv(df_cond):
    
    cat1 = []
    cat2 = [] 
    cat3 = [] 
    cat4 = []
    cat5 = []
    
    fname1 = cond_dir + 'cat1/consent_sub_section.csv'
    fname2 = cond_dir + 'cat2/consent_sub_section.csv'
    fname3 = cond_dir + 'cat3/consent_sub_section.csv'
    fname4 = cond_dir + 'cat4/consent_sub_section.csv'
    fname5 = cond_dir + 'cat5/consent_sub_section.csv'
    
    df_sub = get_sub_headers() 
    pd.set_option('display.max_rows', None)
#    print(df_sub)
#    print(df_cond)
    for i in range(len(df_cond)):

#        cond_cat = df_sub[df_sub.Sub_Header == df_cond.iloc[i,1]]
        for j in range(len(df_sub)):
#            print(f"Cond: {df_cond.iloc[i,1]} Sub: {df_sub.iloc[j,0]}")
            if df_cond.iloc[i,1] == df_sub.iloc[j,0]:

                fields = [df_cond.iloc[i,0],df_cond.iloc[i,1],df_sub.iloc[j,1],df_cond.iloc[i,2]]
#                print(fields)
                if df_sub.iloc[j,1] == 1:
                    cat1.append(fields)
                elif df_sub.iloc[j,1] == 2:
                    cat2.append(fields)
                elif df_sub.iloc[j,1] == 3:
                    cat3.append(fields)
                elif df_sub.iloc[j,1] == 4:
                    cat4.append(fields)
                elif df_sub.iloc[j,1] == 5:
                    cat5.append(fields)
                else:
                    pass            
    

    df1 = pd.DataFrame(cat1,columns=['Textfile','Sub_Header','Cond_Category','Sub_Section'])
    df1.to_csv(fname1,encoding='utf-8',index=False,mode='w') 
    logging.info(' write_csv CSV: ' + fname1)
    
    df2 = pd.DataFrame(cat2,columns=['Textfile','Sub_Header','Cond_Category','Sub_Section'])
    df2.to_csv(fname2,encoding='utf-8',index=False,mode='w') 
    logging.info(' write_csv CSV: ' + fname2)
    
    df3 = pd.DataFrame(cat3,columns=['Textfile','Sub_Header','Cond_Category','Sub_Section'])
    df3.to_csv(fname3,encoding='utf-8',index=False,mode='w') 
    logging.info(' write_csv CSV: ' + fname3)
    
    df4 = pd.DataFrame(cat4,columns=['Textfile','Sub_Header','Cond_Category','Sub_Section'])
    df4.to_csv(fname4,encoding='utf-8',index=False,mode='w') 
    logging.info(' write_csv CSV: ' + fname4 )
    
    df5 = pd.DataFrame(cat5,columns=['Textfile','Sub_Header','Cond_Category','Sub_Section'])
    df5.to_csv(fname5,encoding='utf-8',index=False,mode='w') 
    logging.info(' write_csv CSV: ' + fname5)

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
                search_result = ''
                return False
            else:
                logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' search result is ' + str(sub_header_search)[0:80] + ' in text')
                search_result = str(sub_header_search.group(0))

#            print(f"Textfile: {textfile} Sub Header: {bookend1}")
            fields = [textfile,bookend1,search_result]
            conditions.append(fields)
        else:
            logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' missing bookends in search string' + str(sub_header_search) + ' in text')
            result = False      
    if conditions != []:
        result = conditions
    return result



def search_line(textfile,sub_header,line,matchno,i):  # Note! no point matching for line feeds prior to this line
    
#    pattern = r'(\b)' + sub_header + r'(\s*\n)'
#    pattern = regex.compile(pattern,regex.DOTALL) 
#    search = pattern.search(line)
    pattern = r'(\n+\s*)' + sub_header + r'(\s*\n)'
    search = regex.search(pattern,line,regex.DOTALL)

#    if i == 6 or i == 12:
#        print(f'Line: {i} pattern: {pattern}, line text: {line}')
    if search != None:
        section_matched = True
        logging.info(inspect.stack()[0][3] + '   TEXT: ' + os.path.basename(textfile) + ' Found ' + matchno + ' sub header: ' + str(pattern) + ' on line: ' + str(i))
#        print(textfile, " matched ", search)
        return pattern  
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
    
#    print(bookends)
    return result





def get_conditions(textfiles):

    #1. extract and categorise conditions

    df_cond1 = pd.DataFrame(columns=['Textfile','Sub_Header','Sub_Section'])
    df_cond = pd.DataFrame(columns=['Textfile','Sub_Header','Sub_Section'])
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
                                                         # DataFrame ==> searchtexts = [textfile,bookend1,search_result]
        if searchtexts != False:

            df_cond1 = pd.DataFrame(searchtexts,columns=['Textfile','Sub_Header','Sub_Section'])
            df_cond  = df_cond.append(df_cond1)
            
        logging.info(inspect.stack()[0][3] + ' Finished processing ' + textfiles[i] + ' at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
 
    return df_cond



def get_sub_headers():
    df_sub = pd.read_csv(csv_dir + 'dict_cat_sub_headers.csv',header=0)
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
    
    
    
    df_conditions = get_conditions(textfile_paths) #TODO
    #df_conditions = get_conditions(["/home/admin/dockers/masters/data/pdfminer/search/MP11_0047.txt"],df_subs)  #MP06_0021-Mod-3.txt
    write_ok = write_csv(df_conditions)
    
    #textfile_paths = pd.DataFrame(get_textfile_paths(textfiles))
    logging.info(inspect.stack()[0][3] + ' Logging ended at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

if __name__ == "__main__":
    main()  



## defunct


