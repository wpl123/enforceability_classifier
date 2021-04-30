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
logs_dir = "/home/admin/dockers/masters/data/cond_cat/logs/"
files_dir = "/home/admin/dockers/masters/data/pdfminer/search/"
search_dir = "/home/admin/dockers/masters/data/cond_cat/search/"
cond_dir = "/home/admin/dockers/masters/data/cond_cat/"


def get_lines(iterable):
#    print(iterable)            # https://stackoverflow.com/questions/323750/how-to-access-the-previous-next-element-in-a-for-loop#323910
    iterator = iter(iterable)
    prev_item = None
    current_item = next(iterator)  # throws StopIteration if empty.
    for next_item in iterator:
        yield (prev_item, current_item, next_item)
        prev_item = current_item
        current_item = next_item
    yield (prev_item, current_item, None)



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
    
#    fname1 = cond_dir + 'cat1/pred_consent_sub_section.csv'
#    fname2 = cond_dir + 'cat2/pred_consent_sub_section.csv'
#    fname3 = cond_dir + 'cat3/pred_consent_sub_section.csv'
#    fname4 = cond_dir + 'cat4/pred_consent_sub_section.csv'
#    fname5 = cond_dir + 'pred_consent_sub_section.csv'

    fname1 = cond_dir + 'cat1/consent_sub_section.csv'
    fname2 = cond_dir + 'cat2/consent_sub_section.csv'
    fname3 = cond_dir + 'cat3/consent_sub_section.csv'
    fname4 = cond_dir + 'cat4/consent_sub_section.csv'
    fname5 = cond_dir + 'consent_sub_section.csv'
    
    df_sub = get_sub_headers() 
    pd.set_option('display.max_rows', None)

    for i in range(len(df_cond)):

#        cond_cat = df_sub[df_sub.Sub_Header == df_cond.iloc[i,1]]
        for j in range(len(df_sub)):
#            print(f"Cond: {df_cond.iloc[i,1]} Sub: {df_sub.iloc[j,0]}")
            if df_cond.iloc[i,1] == df_sub.iloc[j,0]:

                fields = [df_cond.iloc[i,0],df_cond.iloc[i,1],df_sub.iloc[j,1],df_cond.iloc[i,2]]
               
                if df_sub.iloc[j,1] == 1:
                    cat1.append(fields)
                elif df_sub.iloc[j,1] == 2:
                    cat2.append(fields)
                elif df_sub.iloc[j,1] == 3:
                    cat3.append(fields)
                elif df_sub.iloc[j,1] == 4:
                    cat4.append(fields)
                else:
                    pass            
    

    df1 = pd.DataFrame(cat1,columns=['Textfile','Sub_Header','Cond_Category','Sub_Section'])
    df1.to_csv(fname1,encoding='utf-8',index=False,mode='w') 
    logging.info(inspect.stack()[0][3] + ' write_csv CSV: ' + fname1)
    
    df2 = pd.DataFrame(cat2,columns=['Textfile','Sub_Header','Cond_Category','Sub_Section'])
    df2.to_csv(fname2,encoding='utf-8',index=False,mode='w') 
    logging.info(inspect.stack()[0][3] + ' write_csv CSV: ' + fname2)
    
    df3 = pd.DataFrame(cat3,columns=['Textfile','Sub_Header','Cond_Category','Sub_Section'])
    df3.to_csv(fname3,encoding='utf-8',index=False,mode='w') 
    logging.info(inspect.stack()[0][3] + ' write_csv CSV: ' + fname3)
    
    df4 = pd.DataFrame(cat4,columns=['Textfile','Sub_Header','Cond_Category','Sub_Section'])
    df4.to_csv(fname4,encoding='utf-8',index=False,mode='w') 
    logging.info( ' write_csv CSV: ' + fname4 )
    
    
    df_cond.to_csv(fname5,encoding='utf-8',index=False,mode='w') 
    logging.info(inspect.stack()[0][3] + ' write_csv CSV: ' + fname5)

    return True  # need to check status of file     


# Separate each sub_condition into its own line in the CSV file
def separate_conditions(textfile,full_conditions):          # full_conditions = [textfile,sub_header1,final_text]
    
    sub_conds = []
    pattern = '[0-9A-Za-z,:;\(\)\-\'\"\/\s]+[.][\s]*[\n]*'

    for full_condition in full_conditions:

        i = 0 
        for match in regex.findall(pattern, full_condition[2]):
 
            match = regex.sub(r'\n','',match)                      # remove the last of the newlines
            fields = [full_condition[0],full_condition[1],match]
            sub_conds.append(fields)
            i = i + 1
            if i == 2:                                             # Only extract maximum of 3 sentences per condition
                break
        
    return sub_conds




def clean_text(textfile,text):

    #1. Remove footers 
    text = regex.sub(r'NSW Government','',text)
    text = regex.sub(r'Department of Planning\, Industry and Environment','',text)
    text = regex.sub(r'Planning\, Industry & Environment','',text)
    text = regex.sub(r'Department of Planning & Environment','',text)
    text = regex.sub(r'Department of Planning and Environment','',text)
    text = regex.sub(r'Department of Planning','',text) 
    text = regex.sub(r'Consolidated version','',text)

    
    text = regex.sub(r'!\"#$%&\(\)*\+\,\-\/:;<=>\?@\[\\\]\^_\`\{\|\}~','',text)
#    text = regex.sub(r'\"','',text)
#    text = regex.sub(r'\,','',text)
#    text = regex.sub(r'No\.','No',text)
    text = regex.sub(r'\’','',text)
    
#   text = regex.sub(r'•.*','',text,regex.DOTALL)   
    
    
    
    # Remove section numbers and page numbers
    text = regex.sub(r'(\n*[0-9][0-9]*\.?\s*\n)','',text)
    text = regex.sub(r'(\n\-\s[0-9][0-9]*\s\-(\s\n)*)','',text)
    text = regex.sub(r'[0-9][A-Z]\.','',text)
    text = regex.sub(r'[0-9][0-9]*\.','',text)
#    text = regex.sub(r'(\n\n+)','\n',text)
    
    #2. Remove Tables
    if regex.search("Table",text) != None:
        pattern = '(\A.*(?=Table))'
        table_pattern = regex.compile(pattern,regex.DOTALL)    
        table_search = table_pattern.search(text)
        if table_search != None:
            text = str(table_search.group(0))
            
    
    #3. Remove Notes
    if regex.search("Note",text) != None:
        pattern = '(\A.*(?=Note))'
        table_pattern = regex.compile(pattern,regex.DOTALL)    
        table_search = table_pattern.search(text)
        if table_search != None:
            text = str(table_search.group(0))


    #3. Dot points (remove all characters to the end of the condition)
    if regex.search("•",text) != None:
        pattern = '(\A.*(?=•))'
        table_pattern = regex.compile(pattern,regex.DOTALL)    
        table_search = table_pattern.search(text)
        if table_search != None:
            text = str(table_search.group(0))
              


#    logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' Cleaning Text ')    
    return text



def search_text(bookends,text):  # conditions = [textfile, bookend1, bookend2]

    conditions = []
    for args in bookends:

        textfile = str(args[0])
        bookend1 = str(args[1])
        bookend2 = str(args[2])
        sub_header1 = str(args[3])

        if bookend1 != "" and bookend2 != "":

#            pattern = '(?<=' + bookend1 + ').*(?=' + bookend2 + ')'
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

#            print(f"Textfile: {textfile} Sub Header: {sub_header1}")

            final_text = clean_text(textfile,search_result)
            fields = [textfile,sub_header1,final_text]
            conditions.append(fields)
        else:
            logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' missing bookends in search string' + str(sub_header_search) + ' in text')
            result = False      
    if conditions != []:
        result = conditions
    return result



def search_line(textfile,sub_header,prev_line,curr_line,next_line,matchno,i):  # Note! no point matching for line feeds prior to this line
    
    search_failed = 'SearchFail'
    #skip 1st line then check for newlines above and below the sub section heading
    if i != 1 and regex.search(r'(\n\s*)',prev_line) == None and regex.search(r'(\n\s*)',next_line) == None:
        return search_failed

    pattern = r'(\b)' + sub_header + r'(\s*\n)'
    search = regex.match(pattern,curr_line,regex.DOTALL)

#    if i == 1:
#        logging.info(inspect.stack()[0][3] + '   TEXT: ' + os.path.basename(textfile) + ' Searching using ' + str(pattern))

    if search != None:
        section_matched = True
        logging.info(inspect.stack()[0][3] + '   TEXT: ' + os.path.basename(textfile) + ' Found ' + matchno + ' sub header: ' + str(pattern) + ' on line: ' + str(i))
#        print(textfile, " matched ", search)
        return pattern  
    else:
#        logging.info(inspect.stack()[0][3] + '   TEXT: ' + os.path.basename(textfile) + matchno + ' Pattern ' + str(pattern) + ' not found on line: ' + str(i))
        return search_failed




def get_bookends(textfile): 
    
    result = []
    bookends = []
    bookend1 = ""
    bookend2 = "SearchFail"
    first_sub_header_matched = False
    second_sub_header_matched = False
    end_of_file = False
    previous_sub_header = ""
    sub_header1 = ""
    sub_header2 = ""
    df_sub = get_sub_headers()     
    i = 0
    found_sub_headers = []

    try:
        with suppress(BufferError):
            doc1 = open(textfile,'r') #,encoding='utf8'
            lines = doc1.readlines()
            doc1.close()
    
        
        for prev_line,curr_line,next_line in get_lines(lines):   # Read each previous, current and next line in the text document 

            i = i + 1
            
            # re-use bookend2 for bookend1 on the next iteration
            if (bookend2 != "SearchFail") & (bookend1 != bookend2):
                bookend1 = bookend2
                sub_header1 = sub_header2
                logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' Convert bookend2 ' + bookend2 + ' to bookend1 ')
                first_sub_header_matched = True

            # executed on the first line of data only
            if first_sub_header_matched == False:

            # Loop through the sub heading and check for first sub_header in the current line 
                for j in range(len(df_sub)):
                    # Skip already matched sub headers    
                    if df_sub.iloc[j,0] != '':    
                        sub_header = df_sub.iloc[j,0]
                        
                    else:
                        continue    
                    
                    #Check for sub_header
                    bookend1 = search_line(textfile,sub_header,prev_line,curr_line,next_line,"first",i) 
                    if bookend1 != "SearchFail":
                        
                        first_sub_header_matched = True
                        sub_header1 = df_sub.iloc[j,0]
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
                    bookend2 = search_line(textfile,sub_header,prev_line,curr_line,next_line,"second",i) 
                    if bookend2 != "SearchFail":
#                        print(f"post search second sub_header {sub_header}")
                        logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' Second sub header matched! ' + sub_header + ' ')
                        second_sub_header_matched = True
                        sub_header2 = df_sub.iloc[j,0]
                        end_line = i
                        #remove the sub_header so it wont get matched as the first sub header again
                        df_sub.iloc[j,0] = '' 
                        break  

            #Accumulate conditions for this text document            
            if second_sub_header_matched == True:
                fields = [textfile,bookend1,bookend2,sub_header1]
                bookends.append(fields)
                first_sub_header_matched = False
                second_sub_header_matched = False

        else: #End of for loop and reached EOF. Set bookend2 to the EOF i.e. \Z
            
            logging.info(inspect.stack()[0][3] + ' TEXT: ' + os.path.basename(textfile) + ' Second sub header not matched! Matching EOF ')
            second_sub_header_matched = True
            bookend2 = "\Z"
            end_line = i
            fields = [textfile,bookend1,bookend2,sub_header1]
            bookends.append(fields)
        
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
        with suppress(BufferError):
            doc2 = open(textfile,'r') #,encoding='utf8'
            text = doc2.read()
            doc2.close()
     
        if bookends != '':
            result = bookends,text
        else:
            result = False, False        
    
   
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
           
            sub_conditions = separate_conditions(str(textfiles[i]),searchtexts)

            df_cond1 = pd.DataFrame(sub_conditions,columns=['Textfile','Sub_Header','Sub_Section'])
            df_cond  = df_cond.append(df_cond1)
            
        logging.info(inspect.stack()[0][3] + ' Finished processing ' + textfiles[i] + ' at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
 
    return df_cond



def get_sub_headers():
    df_sub = pd.read_csv(csv_dir + 'dict_cat_sub_headers.csv',header=0)
    return df_sub  



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
    df_text = pd.read_csv(csv_dir + 'train.csv')                     # 'pred.csv'
    textfile_paths = get_textfile_paths(df_text)
    return df_text, textfile_paths




def main():

    setupLogging()
    df_test, textfile_paths = get_textfiles()
    
    
    
    df_conditions = get_conditions(textfile_paths) #TODO
    #df_conditions = get_conditions(["/home/admin/dockers/masters/data/pdfminer/search/MP11_0047.txt"])  #MP06_0021-Mod-3.txt
    write_ok = write_csv(df_conditions)
    print(write_ok)
    #textfile_paths = pd.DataFrame(get_textfile_paths(textfiles))
    logging.info(inspect.stack()[0][3] + ' Logging ended at ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

if __name__ == "__main__":
    main()  



## defunct


