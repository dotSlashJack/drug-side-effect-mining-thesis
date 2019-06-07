"""
    -*- coding: utf-8 -*-
    This script is written in python 3 for both Apple and Windows machines
    written by Jonathan Gomez Martinez (December 2017)
    modified  by Gabriel Wang (February 2018)
    modified by Jian Chen (Jan 2019)
    modified by Roberto Franzosi (January 2019)
    modified by Jack Hester (January, February 2019)
    modified by Josh Karol (March 2019)
    modified by Jack Hester (March 2019)

        This procedure takes *.txt files and runs StanfordCoreNLP to produce ConLL files for each individual file.
        It then creates a merged ConLL file including all of the ConLL tables in a single ConLL file arguments:
        Stanford Core NLP Path: The first argment is the installlation path of stanford corenlp package
        Corpus TXT files Path: The second argument should be the path to the *.txt files.
        Filename/Output path
            The third argument can be a specific file name in the Corpus TXT files Path or the OutputPath
        OutputPath: The third argument should be the folder where the user would like his/her ConLL files saved
        Memory: The fourth argument should be an integer value (1, 2, 3, 4, 5; try 4 first) specifying how much memory (RAM) a user is willing to give to CoreNLP
            More memory can lead to quicker runtime on large *.txt files
        mergeFiles: A boolean specifying whether or not to run the merge algorithm with 1 meaning yes and 0 meaning no
        getDate: A boolean specifying whether or not to run the date grabbing algorithm with 1 meaning yes and 0 meaning no
            Required parameter if running merge files algorithm
        Separator: A specified separator in the file name that indicates the start of a date (e.g., The New York Times_12-21-1878; the separator is _)
            Required parameter if running date grabbing algorithm
        DateFieldLocation: The date start location (e.g., The New York Times_12-21-1878 the date DateFieldLocation is 2; the second field in the file with fields separated by _; 
                The New York Times_Page 1_12-21-1878 the date start location is 3)
            Required parameter if running date grabbing algorithm
        DateFormat: The date format provided
            Date formats: mm-dd-yyyy; dd-mm-yyyy; yyyy-mm-dd; yyyy-dd-mm; yyyy-mm; yyyy;
            Required parameter if running date grabbing algorithm
    TODO: Modify the all-files-in-dir mode & one-file mode, the current version is really bad practice
    Useful debug tip: well, you may be in trouble if you are trying to debug the arguments

    But just start with enumerating the sys.argv

    Command prompt start
    cd "C:\\Program files (x86)\\PC-ACE\\NLP\\CoreNLP"
    "" around paths are necessaryy when the path includes spaces
    Python StanfordCoreNLP_GUI.py "C:\\Program files (x86)\\PC-ACE\\NLP\\stanford-corenlp-full-2018-10-05" "C:\\Users\rfranzo\\Documents\\ACCESS Databases\\PC-ACE\\NEW\\DATA\\CORPUS DATA\\Sample txt" "C:\\Users\rfranzo\\Desktop\\NLP_output" 4 1 1 _ 2 mm-dd-yyyy

"""
from pycorenlp import StanfordCoreNLP
import os
import glob
import time
import datetime
import pandas as pd
import subprocess
import sys
import numpy as np
import io
import re
from collections import OrderedDict
from unidecode import unidecode
import socket
from contextlib import closing
import ntpath
import random
from tkinter import filedialog
import tkinter.messagebox as mb
import tkinter as tk
from tkinter import DISABLED
import shutil
from sys import platform


# getting and setting current directory path to make it easier on user

dir_path = os.path.dirname(os.path.realpath(__file__))

os.chdir(dir_path)



##%%
"""
def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex((host, port)) == 0:
                print ("Port is open")
            else:
                print ("Port is not open")
"""

def get_open_port():
    try:
        # function to find a open port on local host
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # next line should allow port's socket to be re-used later even if program crashes
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("",0))
        s.listen(1)
        print('printing getsockname below')
        print(s.getsockname())
        port = s.getsockname()[1]
        s.close()
        return port
    except Exception as e:
        print ("\nSocket error was found:\n "+e.__doc__)
        sys.exit(0)

def split_file(input_path):
    someTooLarge = False
    # gather the docs
    docList = []
    for f in os.listdir(input_path):
        if not f[:2] == '~$': # ignore the temporary files
            if f[-4::]=='.txt':# check if it is a .txt file
                docList.append(os.path.join(input_path,f))
    # check the docs
    for file in docList:
        f = open(file, 'r')
        doc = f.read()
        length = len(doc)
        print('found file of length: ', str(length))
        if(length>100000): # check if file is too long for Stanford CoreNLP
            someTooLarge = True
            splitLocation = 99998
            splitList = [] # list of to break files up later on
            while splitLocation<length:
                # check if there's a punctuation mark so sentences aren't split up
                if doc[splitLocation]=='.' or doc[splitLocation]=='?' or doc[splitLocation]=='!':
                    splitList.append(splitLocation+1)
                    newSplit = splitLocation+99998
                    if newSplit <= length:
                        splitLocation = splitLocation+99998
                    else: # we've gotten through the whole file, making sure no index error
                        splitLocation = length
                        splitList.append(splitLocation)
                        #break
                else:
                    splitLocation = splitLocation-1
            print(splitList)
            # writing sections that were split to new files
            for s in range(0, len(splitList)):
                filenameStr = file.split('.txt')[0]+'_'+str(s+1)+'.txt'
                newFileName = os.path.join(input_path, filenameStr)
                newFile = open(newFileName, 'w+')
                if s-1 < 0:
                    newFile.write(doc[0:splitList[s]])
                    #print("0 index ran")
                else:
                    newFile.write(doc[splitList[s-1]:splitList[s]])
                    #print("main newfile ran")
                newFile.close()
            #newDir = os.path.join(input_path, 'removed-files')
            if sys.platform in ['win32','cygwin','win64']:
                newDir = input_path+'\\removed-files'
                #newpath = r'newDir'
                try:
                    os.mkdir(newDir)
                except:
                    print('could not create new directory to move files to, it may already exist. If so files will be moved there.')
                    print(newDir)
                print('splitting')
                splitName = file.split('\\')
                #print('split: ', splitName)
                newfilename = os.path.join(newDir, splitName[len(splitName)-1])
                #print(newfilename)
                try:
                    shutil.move(file, newfilename)
                    print(file, " was moved to ", newDir)
                except Exception as e:
                    print(e.__doc__)
                    print('!!!')
                    print()
                    print('WARNING: we could not remove the original un-split from the input folder due to a permissions error. This may cause issues! If so, remove it yourself.')
                    print()
                    print('!!!')
            else:
                newDir = input_path+'/removed-files'
                try:
                    os.mkdir(newDir)
                except:
                    print('could not create new directory to move files to, it may already exist. If so files will be moved there.')
                    print(newDir)
                print('splitting')
                splitName = file.split('/')
                #newfilename = os.path.join(newDir, splitName[len(splitName)-1])
                newfilename = newDir+'/'+splitName[len(splitName)-1]
                try:
                    shutil.move(file, newfilename)
                    print(file, " was moved to ", newDir)
                except Exception as e:
                    print(e.__doc__)
                    print('!!!')
                    print()
                    print('WARNING: we could not remove the original un-split from the input folder due to a permissions error. This may cause issues! If so, remove it yourself.')
                    print()
                    print('!!!')

    if someTooLarge == True:
        print("Some files were too large for Stanford CoreNLP, so they were split and the original was moved to a sub directory. Split files end in _1, _2, etc. This does NOT mean the program stopped running.")
        if isCLA != True:
            tk.messagebox.showinfo("Notice", "Some files were too large for Stanford CoreNLP, so they were split and the original was moved to a sub directory. Split files end in _1, _2, etc. This does NOT mean the program stopped running.")

def RunCoreNLP(stanford_core_nlp_path, input_path, output_path, assigned_memory, merge_file_flag,get_date_flag=0,sep='_',date_field_position=3,date_format='mm-dd-yyyy',file_name=''):
    #check_socket('localhost',9000)
    
    print('checking files')
    split_file(input_path) # check all files to make sure they aren't too large
    print('checked length')
    
    port = get_open_port() #find a open port for corenlp
    print(port + ' is currently in use')
    #print('see port above')

    stanford_core_nlp_path = os.path.join(stanford_core_nlp_path,'*')

    #TODO: modify this later
    #should be input path, need to talk about this later

    is_path = os.path.isdir(output_path)

    #Check that the input directory contains txt files; exit otherwise

    if len(glob.glob(os.path.join(input_path,"*.txt")))==0:
        print ("There are no txt files in the input directory " + str(input_path) + ". Program will exit.")
        sys.exit(0)

    command = ['java','-mx'+str(assigned_memory)+'g','-cp', str(stanford_core_nlp_path),'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-port', str(port),'timeout','15000'] #was 999999 earlier

    try: #remove this try later, it's for debugging purposes
    #Launch CoreNLP server, allowing us to run *.txt files without re-initializing CoreNLP
        with open(os.devnull, 'w') as fp:
            server = subprocess.Popen(command, stdout=fp) #avoid printing the entire document
            #server = subprocess.Popen(command)  #this will print the entire document
        time.sleep(5)#wait for the subprocess to set up the server
    except Exception as e:
        print ("\nError was found when running popen command:\n "+e.__doc__)
        sys.exit(0)


    """
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        print ("")
        sys.exit(0)"""

    nlp = StanfordCoreNLP('http://localhost:'+str(port))  #Attach the server to a variable for cleaner code
    #nlp = StanfordCoreNLP('http://localhost:8080')  #Attach the server to a variable for cleaner code
    if(is_path): #This is the all-files-in-dir mode
        InputDocs=[]
        for f in os.listdir(input_path):
            if not f[:2] == '~$': # ignore the temporary files
                if f[-4::]=='.txt':# check if it is a .txt file
                    InputDocs.append(os.path.join(input_path,f))
    else: # one-file mode
        InputDocs = [os.path.join(input_path,file_name)]

    startTime = time.localtime()
    print("")
    print("Started running Stanford CoreNLP at " + str(startTime[3]) + ':' + str(startTime[4])) #Prints start time for future reference
    # get statuses of merging and date for alerts
    if merge_file_flag == 1:
        mergeStatus = "merging on"
        if get_date_flag == 1:
            dateStatus = "date gathering on."
        else:
            dateStatus = "no date gathering."
    else:
        mergeStatus = "merging off"
        dateStatus = "date gathering off."
    if isCLA!=True:
        tk.messagebox.showinfo("Stanford CoreNLP has started","Started running Stanford CoreNLP at " + str(startTime[3]) + ':' + str(startTime[4]) + " with "+mergeStatus+" and "+dateStatus+" You can check its status in your command prompt/terminal.")
    #The loop below opens each *.txt file in the input directory and passes the text to our local CoreNLP server.
    #   The server then returns our ConLL table in a tab separated format which is then saved as a *.ConLL file
    #   Opened files are closed as soon as they are no longer necessary to free-up resources

    i = 0.0
    CorrectlyProcessedFileNames = []
    for file in InputDocs:
        server.poll()
        F = io.open(file, 'r', encoding='utf-8',errors='ignore')
        text = F.read()
        text = text.encode('utf-8')
        #print(text)

        F.close()
        # x: ntpath

        #x = file[len(Path)::] # Only keep the file name with .txt

        #print ("......",x, ntpath.dirname(file),ntpath.basename(file))
        x = ntpath.basename(file)



        #CorrectlyProcessedFileNames.append(x)

        print("")
        print("Parsing file: " + x)
        print("")
        #print(x.find('_'))

        try:
            udata = text.decode("utf-8")
            text = udata.encode("ascii", "ignore")
           
            
            #print (text)
            output = nlp.annotate(text.decode('utf-8'), properties={        #Passes text and preferences (properties) to CoreNLP
                'annotators': 'tokenize,ssplit,pos,lemma, ner,parse', 'outputFormat': 'conll', 'timeout': '999999', 'outputDirectory': output_path, 'replaceExtension': True})

           # print(output)
            # Replace normalized paranthese back
            output = str(output).replace("-LRB-","(").replace("-lrb-","(") .replace("-RRB-",")") .replace("-rrb-",")") .replace("-LCB-","{") .replace("-lcb-","{") .replace("-RCB-","}") .replace("-rcb-","}") .replace("-LSB-","[") .replace("-lsb-","[") .replace("-RSB-","]") .replace("-rsb-","]")
            
            print("Writing CoNLL table: " + x)

            text_file = io.open(os.path.join(output_path,x) + ".conll", "w", encoding='utf-8')
            text_file.write(output)             #Output *.ConLL file
            text_file.close()
            print(str(100 * round(float(i) / len(InputDocs), 2)) + "% Complete") #Rough progress bar for reference mid-run
            CorrectlyProcessedFileNames.append(x)
            i += 1

        except Exception as e:
            print("")
            print("Could not create CoNLL table for " + "\""+x+"\""+'. Message returned by Stanford server: '+"\""+str(e)+"\"")
            print("")
            server.poll()

    endTime = time.localtime()
    server.kill() #Server is killed before entire procedure is completed since we no longer need it
    print("")
    
    if merge_file_flag != 1:
        print("Finished running Stanford CoreNLP at " + str(endTime[3]) + ':' + str(endTime[4]))    #Time when ConLL tables finished computing, for future reference
        if isCLA!=True: 
            tk.messagebox.showinfo("Stanford CoreNLP has finished", "Finished running Stanford CoreNLP at " + str(endTime[3]) + ':' + str(endTime[4]) + " with "+mergeStatus+" and "+dateStatus)
    if (len(CorrectlyProcessedFileNames) ==0):
        print(str(len(InputDocs)) + " input documents were processed. No CoNLL table was produced! Program will exit.")
        sys.exit(0)

    #Here we merge all of the previously computed ConLL tables into a single merged ConLL table
    ConLL = glob.glob(os.path.join(output_path,"*.conll"))   #Produce a list of ConLL tables in the output directory

    #The loop below opens each *.ConLL file in the ouput directory, checks that the name corresponds to the processed txt filename (excluuding all other CoNLL tables)
    #   and pulls the contents into memory, creating a running table of concatenated tables. Opened files are closed after being pulled into memory
    #   to preserve resources
    if merge_file_flag == 1:
        startTime = time.localtime()
        print ("")
        print("Started merging at " + str(startTime[3]) + ':' + str(startTime[4]))  #Time when merge started, for future reference
        merge = None    #Initialize an empty variable to assure the  new merged table is in fact new
        MergedDocNum = 1 #the N input documents in the merged CoNLL table are numbered 1 through N

        for table in ConLL:
            lineNum = 1
            x = ntpath.basename(table)[:-6] #get the table name without .CoNLL so that the name can be compared with input document name
            if x in CorrectlyProcessedFileNames:
                print("")
                print("merging table: " + x)    #Prints the name of the table being worked on
                print("")
                if get_date_flag == 1:
                    startSearch = 0
                    iteration = 0
                    while iteration < date_field_position-1:
                        startSearch = x.find(sep, startSearch + 1)
                        iteration += 1
                    altSeparator=".txt"
                    end = x.find(sep, startSearch + 1)
                    if end == -1:
                        end = x.find(altSeparator, startSearch + 1)
                    raw_date = x[startSearch+1:end]

                    #https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior

                    #the strptime command (strptime(date_string, format) takes date_string and formats it according to format where format has the following values:
                    # %m 09 %-m 9 (does not work on all platforms); %d 07 %-d 7 (does not work on all platforms);
                    #loop through INPUT date formats and change format to Python style
                    #print('DATEFORMAT',date_format)

                    try:
                        dateStr = ''
                        if date_format == 'mm-dd-yyyy':
                            date = datetime.datetime.strptime(raw_date, '%m-%d-%Y').date()
                            dateStr = date.strftime('%m-%d-%Y')
                        elif date_format == 'dd-mm-yyyy':
                            date = datetime.datetime.strptime(raw_date, '%d-%m-%Y').date()
                            dateStr = date.strftime('%d-%m-%Y')
                        elif date_format == 'yyyy-mm-dd':
                            date = datetime.datetime.strptime(raw_date, '%Y-%m-%d').date()
                            dateStr = date.strftime('%Y-%m-%d')
                        elif date_format == 'yyyy-dd-mm':
                            date = datetime.datetime.strptime(raw_date, '%Y-%d-%m').date()
                            dateStr = date.strftime('%Y-%d-%m')
                        elif date_format == 'yyyy-mm':
                            date = datetime.datetime.strptime(raw_date, '%Y-%m').date()
                            dateStr = date.strftime('%Y-%m')
                        elif date_format == 'yyyy':
                            date = datetime.datetime.strptime(raw_date, '%Y').date()
                            dateStr = date.strftime('%Y')
                        dateStr = dateStr.replace('/','-')
                        #print(dateStr)

                    except ValueError:
                        print('Error: You might have provided the incorrect date format or the date (' + raw_date + ') in the filename is wrong. Please check!')
                        pass

                    if x == 'mergedConllTables': #Assures that the merged ConLL table is not merged into our new merged ConLL table (in the case of re-running script)
                        continue

                    if merge is None:
                        hold = pd.DataFrame.from_csv(io.open(table, 'rb'), sep='\t', header=None, index_col=False)
                        holdDocNum = pd.DataFrame(OrderedDict( (('MergedDocNum', np.ones(hold.shape[0]) * MergedDocNum) , ('name', x), ('date', dateStr))) ) #np.ones(hold.shape[0]) * MergedDocNum) , ('name', x), ('date', date))) )
                        hold = hold.merge(holdDocNum, left_index=True, right_index=True, how='inner')
                        merge = hold

                    else:
                        hold = pd.DataFrame.from_csv(io.open(table, 'rb'), sep='\t', header=None, index_col=False)
                        holdDocNum = pd.DataFrame(OrderedDict( (('MergedDocNum', np.ones(hold.shape[0]) * MergedDocNum) , ('name', x), ('date', dateStr))) ) #np.ones(hold.shape[0]) * MergedDocNum) , ('name', x), ('date', date))) )
                        hold = hold.merge(holdDocNum, left_index=True, right_index=True, how='inner')
                        merge = pd.concat([merge, hold], axis=0, ignore_index=True)
                    MergedDocNum += 1
                if get_date_flag == 0:
                    if x == 'mergedConllTables': #Assures that the merged ConLL table is not merged into our new merged ConLL table (in the case of re-running script)
                        continue
                    if merge is None:
                        hold = pd.DataFrame.from_csv(io.open(table, 'rb'), sep='\t', header=None, index_col=False)
                        holdDocNum = pd.DataFrame(OrderedDict((('DocNum', np.ones(hold.shape[0]) * MergedDocNum), ('name', x))))
                        hold = hold.merge(holdDocNum, left_index=True, right_index=True, how='inner')
                        merge = hold
                    else:
                        hold = pd.DataFrame.from_csv(io.open(table, 'rb'), sep='\t', header=None, index_col=False)
                        holdDocNum = pd.DataFrame(
                            OrderedDict((('DocNum', np.ones(hold.shape[0]) * MergedDocNum), ('name', x))))
                        hold = hold.merge(holdDocNum, left_index=True, right_index=True, how='inner')
                        merge = pd.concat([merge, hold], axis=0, ignore_index=True)
                    MergedDocNum += 1

        MergedDocNum -= 1
        if MergedDocNum == 0: #no tables were merged
            if (len(ConLL) !=0): #there are CoNLL tables in the output directory
                print("Although there are " + str(len(ConLL)) + " CoNLL tables in your output directory, nore are CoNLL tables for the input txt documents. No merged table produced.")
                sys.exit(0)
            else:
                print ("No CoNLL tables produced for the input txt documents. No merged table produced.")
                sys.exit(0)

        counter = np.arange(1,merge.shape[0]+1)
        merge.insert(7, 'RecordNum', counter)
        sentenceID = 0
        docID = 1
        sentIDs = []

        for i in range(merge.shape[0]):
            if int(merge.iloc[i][8]) > docID:
               docID = docID + 1
               sentenceID = 0
            if(str(merge.iloc[i][0]) == '1'):
                sentenceID += 1
            sentIDs.append(sentenceID)

        merge.insert(9, 'SentenceID', sentIDs)
        merge.to_csv(os.path.join(output_path,"mergedConllTables.conll"), sep='\t', index=False, header=False)    #Outputs merged ConLL table as a *.ConLL file into our output directory
        endTime = time.localtime()

        print("")
        print("Finished merging CoNLL tables at " + str(endTime[3]) + ':' + str(endTime[4]) + ". Merged table exported as: " + os.path.join(output_path,"mergedConllTables.conll"))     #Time when merge finished, for future reference
        if isCLA!=True:
            tk.messagebox.showinfo("Stanford CoreNLP has finished", "Finished running Stanford CoreNLP at " + str(endTime[3]) + ':' + str(endTime[4]) + " with "+mergeStatus+" and "+dateStatus + ". Merged table exported as: " + os.path.join(output_path,"mergedConllTables.conll"))

        if compute_sentence.get()==1:
            startTime = time.localtime()
            if isCLA!=True:
                tk.messagebox.showinfo("Stanford CoreNLP has finished", "Started computing the Sentence table at " + str(startTime[3]) + ':' + str(startTime[4]))

            print ("")
            print("Started computing the Sentence table at " + str(startTime[3]) + ':' + str(startTime[4]))  #Time when merge started, for future reference

            df = pd.read_csv(io.open(os.path.join(output_path,"mergedConllTables.conll"), 'rb'), sep='\t', header=None, index_col=False) # Open ConLL
            rows=[] # Store data
            sent_str = "" # Build string

            #Keep track of variables
            sent_index = df.iloc[0][9]
            doc_id = df.iloc[0][8]
            current_file = df.iloc[0][10]

            for index, row in df.iterrows(): # For every row in the ConLL
                if sent_index == row[9] and current_file==row[10]: # Build the sentence if we are on the same document and sentence
                    if row[6]=="punct":
                        sent_str = sent_str + row[1]
                    else:
                        sent_str = sent_str + " " +row[1]
                else: # End the sentence, add it to the array and move onto the next one
                    arr = [current_file, doc_id, sent_index, sent_str, len(sent_str.split(" ")), len(list(sent_str))] # Save the data
                    rows.append(arr)
                    sent_index = row[9]
                    sent_str = row[1]
                    current_file=row[10]
                    doc_id=row[8]

            # Construct and save the table
            col_names =  ['Document name', 'DocumentID', 'SentenceID', 'Sentence', 'Sentence length (. words-tokens)', 'Sentence length (. characters)']
            df2 = pd.DataFrame(columns = col_names, data=rows)
            df2.to_csv(os.path.join(output_path,"sentence_table.csv"), sep='\t', encoding='utf-8')

            if isCLA!=True:
                tk.messagebox.showinfo("Stanford CoreNLP has finished", "Finished computing the Sentence table at " + str(endTime[3]) + ':' + str(endTime[4])  + ". Sentence table exported as: " + os.path.join(output_path,"sentence_table.csv"))

            print ("")
            print("Finished computing the Sentence table at " + str(endTime[3]) + ':' + str(endTime[4]) + ". Sentence table exported as: " + os.path.join(output_path,"sentence_table.csv"))     #Time when compute sentence tablel finished, for future reference

        sys.exit(0)
    if isCLA == True:
        window.destroy()
        return


#%%

text_label = "For information about this program, hit \"Read Me\"\n To run the program, select the INPUT Stanford CoreNLP and corpus txt files paths, OUTPUT CoNLL table path and hit buttons below.\nTo exit the program, hit \"Quit\" \n\nSTANFORD CoreNLP HAS A LIMIT OF 100,000 CHARACTERS PER FILE. BIGGER FILES MUST BE BROKEN UP INTO SEPARATE FILES AND THEN MERGED."



help_main = \
"""

This Python 3 script will use the Stanford CoreNLP to parse text file(s) (CORPUS) and create CoNLL table(s) in output, one for each txt file in an input directory. An output CoNLL table is basically a csv file with extension .conll. Individual CoNLL tables can be merged together in a single CoNLL table for easy analysis. If input filenames embed dates, these can be saved in the merged output to be analyzed with an Ngrams viewer. Date options are disabled when the Merge option is set to false.
\n
STANFORD CoreNLP HAS A LIMIT OF 100,000 CHARACTERS PER FILE. BIGGER FILES MUST BE BROKEN UP INTO SEPARATE FILES AND THEN MERGED.

"""

#ROBY

#%%

"""

########################

            GUI

#######################

"""

# save paths

# save stanford nlp dir
if os.path.isfile('StanfordNLP-config.txt')==True:
    f=open("StanfordNLP-config.txt", "r")
    coreNLPPath = f.readline()
    f.close()
else:
    coreNLPPath = ''

# save input dir
if os.path.isfile('input-config.txt')==True:
    f=open("input-config.txt", "r")
    inPath = f.readline()
    f.close()
else:
    inPath = ''

# save output dir
if os.path.isfile('output-config.txt')==True:
    f=open("output-config.txt", "r")
    outPath = f.readline()
    f.close()
else:
    outPath = ''


queries_x_cord = 120

label_x_cord = 400 #342
label_x_cord_wn = 375



help_button_x_cord = 50
labels_x_cord = 150
entry_box_x_cord = 350
basic_y_cord = 90
y_step = 50 #40



def exit_window():
    global window
    window.destroy()
    exit()

    

def empty():
    print('empty function for debug')
    return 


"""

msgboxes

"""

#ROBY
def main_msgbox():

    mb.showinfo(title='Introduction', message=help_main)

    

def helper_buttons(canvas,x_cord,y_cord,text_title,text_msg):

    

    def msg_box():

        mb.showinfo(title=text_title, message=text_msg)

    tk.Button(canvas, text='? HELP', command=msg_box).place(x=x_cord,y=y_cord)



"""

button-associated functions

"""
#out_file_path = ''
def select_output_dir():
    global output_file_path
    out_file_path = filedialog.askdirectory(initialdir = os.getcwd())
    output_file_path.set(out_file_path)
    print(out_file_path)
    return out_file_path


#stan_file_path = ''
def select_stanford_corenlp_dir():
    global stanford_core_NLP_path
    stan_file_path = filedialog.askdirectory(initialdir = os.getcwd())
    stanford_core_NLP_path.set(stan_file_path)
    print(stan_file_path)
    return stan_file_path


#in_file_path = ''
def select_input_path():
    global input_file_path
    in_file_path = filedialog.askdirectory(initialdir = os.getcwd())
    input_file_path.set(in_file_path)
    print(in_file_path)
    return in_file_path

def memory_dropdown():
    print(assigned_memory.get())

def test_input_and_run_query():
    CoreNLPPath = stanford_core_NLP_path.get()

    Path = input_file_path.get()
    Output = output_file_path.get()
    mem = memory_var.get()

    mergeFiles = merge_file_or_not.get()

    getDate = find_date_or_not.get()

    separator = separator_var.get()

    DateFieldLocation = date_loc_var.get()
    DateFormat = date_format.get()

    print(CoreNLPPath, Path, Output,mem,mergeFiles,getDate,separator,DateFieldLocation,DateFormat)


    try:
        RunCoreNLP(CoreNLPPath, Path, Output,mem,mergeFiles,getDate,separator,DateFieldLocation,DateFormat)
    except Exception as e:
        print ('Unexpected Error! Check your input and try again.')
        print (e.__doc__)
        sys.exit(0)
#return


window = tk.Tk()

window.title('Stanford CoreNLP GUI')

window.geometry('1250x700')


def get_tips():

    chosenTipsFile = str(tips_dropdown_field.get())

    if chosenTipsFile == 'Part of Speech Tags (POSTAGS)':

        tips_filename = "TIPS__11__Part of Speech Tags (POSTAG).pdf"

    elif chosenTipsFile == 'CoNLL Table':

        tips_filename = "TIPS__11__Stanford CoreNLP CoNLL table.pdf"

    elif chosenTipsFile == 'Stanford Dependency Relation (DEPREL)':

        tips_filename = "TIPS__11__Stanford CoreNLP Dependency Relations (DEPREL).pdf"

    else:

        tips_filename = ''

    # get final path and open with system viewer

    win_tipsSubdir = 'TIPS\\'

    unix_tipsSubdir = 'Tips/'

    win_tips_path = dir_path+'\\'+win_tipsSubdir+tips_filename # windows string

    tips_path = unix_tipsSubdir+tips_filename # macs and linux string

    # check platform they're using and if the selected TIPS file exists

    if platform in ['win32','cygwin']:

        if os.path.isfile(win_tips_path)!=True:

            tk.messagebox.showinfo("TIPS warning", "The tips file "+win_tips_path+" could not be found in your TIPS directory.")

            print('error opening tips file')

        else:

            os.system('start "" "'+win_tips_path+'"')

            print('Windows TIPS file successfully opened')

    else:

        if os.path.isfile(tips_path)!=True:

            tk.messagebox.showinfo("TIPS warning", "The tips file "+tips_path+" could not be found in your TIPS directory.")

            print('error opening tips file')

        else:

            call(['open',tips_path])

            print('unix TIPS file successfully opened')



# import tips files if available

def checkTipsDir():

    win_tipsSubdir = 'TIPS\\'

    unix_tipsSubdir = 'Tips/'

    if os.path.isdir(win_tipsSubdir) or os.path.isdir(unix_tipsSubdir):

        print('Successfully loaded TIPS files')

    else:

        tk.messagebox.showinfo("TIPS warning", "The script could not find a TIPS subdirectory. TIPS should be stored in a subdirectory called TIPS of the directory where the StanfordCoreNLP_GUI.py script is stored: " + str(dir_path))

        tips_menu_lb.configure(state='disabled')

        unix_tipsSubdir = 'no-tips'

        win_tipsSubdir = 'no-tips'

        print('returning to main window test')

        window.focus()

        window.focus_force()

checkTipsDir()


# TIPS menu var

tips_dropdown_field = tk.StringVar()
tips_dropdown_field.set('Open TIPS files')

# calling back tips menu ot see if it's been updated to enable opening tips

def check_tips(*args):

    get_tips()

tips_dropdown_field.trace("w", check_tips)

def main_msgbox():

    mb.showinfo(title='Introduction', message=help_of_program)

    

def CoreNLP_msgbox():

    mb.showinfo(title='HELP: Stanford CoreNLP',

                           message=help_CoreNLP)


def corpus_msgbox():

    mb.showinfo(title='HELP: Corpus',

                           message=help_corpus)    

def output_msgbox():

        mb.showinfo(title='HELP: Output folder',

                           message=help_output_folder)  

        
def memory_msgbox():

        mb.showinfo(title='HELP: Memory size',

                           message=help_memory_size)  

        
def sentence_table_msgbox():

        mb.showinfo(title='HELP: Sentence table',

                           message=help_sentence_table)

        
def merge_msgbox():

        mb.showinfo(title='HELP: Merge ConLL tables',

                           message=help_merge)

        

def date_in_filename_msgbox():

        mb.showinfo(title='HELP: Filename contains date',

                           message=help_date_in_filename)


#ROBY
def date_format_msgbox():

        mb.showinfo(title='HELP: Date format',

                           message=help_date_format)

def date_separator_msgbox():

        mb.showinfo(title='HELP: Character used to separate date in filename',

                           message=help_date_separator)


def date_position_msgbox():

        mb.showinfo(title='HELP: Position of date in filename',

                           message=help_date_position)

"""
variables
"""

global stanford_core_NLP_path, input_file_path,output_file_path,memory_var,separator_var,date_loc_var,date_format,find_date_or_not,merge_file_or_not

stanford_core_NLP_path = tk.StringVar()
stanford_core_NLP_path.set(coreNLPPath)

input_file_path = tk.StringVar()
input_file_path.set(inPath)

output_file_path = tk.StringVar()
output_file_path.set(outPath)

memory_var = tk.IntVar()
memory_var.set(4)

separator_var = tk.StringVar()
separator_var.set('_')

date_loc_var = tk.IntVar()
date_loc_var.set(2)

date_format = tk.StringVar()
date_format.set('mm-dd-yyyy')

# Create a Tkinter variable

#For more information about a specific button, hit the \"? HELP\" button next to it.

intro = tk.Label(window, anchor = 'w', text=text_label)
intro.pack()

intro_button = tk.Button(window, text='Read Me',command=main_msgbox,width=20,height=2)
intro_button.place(x=150,y=600)

execute_button = tk.Button(window, text='Execute CoreNLP', width=20,height=2, command=test_input_and_run_query)
execute_button.place(x=350,y=600)

quit_button = tk.Button(window, text='QUIT', width=20,height=2, command=exit_window)
quit_button.place(x=550,y=600)

# TIPS menu dropdown and var monitoring

tips_menu_lb = tk.OptionMenu(window,tips_dropdown_field,'CoNLL Table', 'Part of Speech Tags (POSTAGS)', 'Stanford Dependency Relation (DEPREL)')

tips_menu_lb.place(x=750, y=600)


select_input_dir_button=tk.Button(window, width = 30,text='Select Stanford CoreNLP directory', command=select_stanford_corenlp_dir)
select_input_dir_button.place(x=queries_x_cord,y=basic_y_cord)
tk.Label(window, textvariable=stanford_core_NLP_path).place(x=label_x_cord, y= basic_y_cord)

select_input_dir_button=tk.Button(window, width = 30,text='Select INPUT txt corpus directory', command=select_input_path)
select_input_dir_button.place(x=queries_x_cord,y=basic_y_cord+y_step)
tk.Label(window, textvariable=input_file_path).place(x=label_x_cord, y= basic_y_cord+y_step)

select_save_file_button=tk.Button(window, width = 30,text='Select OUTPUT CoNLL table directory', command=select_output_dir)
select_save_file_button.place(x=queries_x_cord,y=basic_y_cord+y_step*2)
tk.Label(window, textvariable=output_file_path).place(x=label_x_cord, y= basic_y_cord+y_step*2)

"""saveNLPButton = tk.Button(window, text="Save directory", command=save_Stanford_to_text)
saveNLPButton.place(x=label_x_cord*2.2, y=basic_y_cord)

saveInButton = tk.Button(window, text="Save directory", command=save_in_to_text)
saveInButton.place(x=label_x_cord*2.2, y=basic_y_cord+y_step)

saveOutButton = tk.Button(window, text="Save directory", command=save_out_to_text)
saveOutButton.place(x=label_x_cord*2.2, y=basic_y_cord+y_step*2.5)"""


#%%
#ROBY

help_of_program = "This Python 3 routine will search all the tokens (i.e., words) related to a user-supplied keyword, found in either FORM or LEMMA of a user-supplied CoNLL table.\n\n You can filter results by specific POSTAG and DEPREL values for both searched and co-occurring tokens (e.g., POSTAG ‘NN for nouns, DEPREL nsubjpass for passive nouns that are subjects.) \n\nIn INPUT the routine expects a CoNLL table generated by the python routine StanfordCoreNLP.py. In OUTPUT the routine creates a tab-separated csv file with a user-supplied filename and path.\n\nIt also displays the same infomation in the command line."

help_CoreNLP = "Please, select the directory where you downloaded the Stanford CoreNLP software. \n\nDON'T FORGET TO TICK THE SAVE CHECKBOX! If you save the Directory you will not need to enter it again next time you run this Python script."

help_corpus = "Please, select the directory where you store your TXT corpus to be analyzed by Stanford CoreNLP.  \n\nDON'T FORGET TO TICK THE SAVE CHECKBOX! If you save the Directory you will not need to enter it again next time you run this Python script."

help_output_folder = "Please, select the directory where Stanford CoreNLP will save output CoNLL table(s). \n\nDON'T FORGET TO TICK THE SAVE CHECKBOX! If you save the Directory you will not need to enter it again next time you run this Python script."

help_memory_size = "Please, select the memory size Stanford CoreNLP will use to compute the CoNLL table. Default = 4. Lower this value if CoreNLP runs out of resources."

help_sentence_table = "Please, check the tickbox if you want to create a sentence table from the CoNLL table."

help_merge = "Please, check the tickbox if you want to create a merge table from the CoNLL table. The MERGE subroutine will create a single CoNLL table from individual tables if the input corpus directory contains multiple TXT files. The merge subroutine will add the following fields to the standard 7 fields of a CoNLL table (ID, FORM, LEMMA, POSTAG, NER, HEAD, DEPREL): RECORD NUMBER, DOCUMENT NUMBER, SENTENCE NUMBER, DOCUMENT NAME (INPUT filename), DATE (if the filename embeds a data).  \n\nMANY OTHER NLP ROUTINES ARE BASED ON THE MERGE TABLE. USE THE MERGE OPTION EVEN WHEN WORKING WITH A SINGLE FILE!"

help_date_in_filename =  "Please, check the tickbox if your filenames embed a date (e.g., The New York Times_12-23-1992). \n\nThe DATE subroutine will add a date field to the merged CoNLL table. The date field will be used by other NLP scripts (e.g., Ngrams). \n\nThe DATE routine runs ONLY when the merge option and the filename embeds date option are ticked."

help_date_format = "Please, select the date format of the date embedded in the filename (default mm-dd-yyyy).  \n\nThe DATE FORMAT option is available ONLY when the merge option and the filename embeds date option are ticked."

help_date_separator = "Please, enter the character used to separate the date field embedded in the filenames from the other fields (e.g., _ in the filename The New York Times_12-23-1992) (default _).  \n\nThe DATE CHARACTER SEPARATOR option is available ONLY when the merge option and the filename embeds date option are ticked."

help_date_position = "Please, select the position of the date field in the filename (e.g., 2 in the filename The New York Times_12-23-1992; 4 in the filename The New York Times_1_3_12-23-1992 where perhaps fields 2 and 3 refer respectively to the page and column numbers).  \n\nThe DATE POSITION option is available ONLY when the merge option and the filename embeds date option are ticked."

help_display = "For informations about this program, hit \"Read Me\"\nTo run the query, fill the following fields and hit \"Run Query\".\nTo exit this program, hit \"Quit\".\n\nAll fields with \'*\' need to be filled."

#%%

"""

check box

"""

def print_checkboxes():


    if compute_sentence.get() == 1:
        sentence_table_checkbox_msg.config(text="A Sentence table will be produced")
    elif compute_sentence.get() == 0:
        sentence_table_checkbox_msg.config(text="No Sentence table will be produced")

    if merge_file_or_not.get() == 1:
        merge_file_checkbox_msg.config(text="A merged CoNLL table will be produced")
    elif merge_file_or_not.get() == 0:
        merge_file_checkbox_msg.config(text="No merged CoNLL table will be produced")
        find_date_or_not.set(0)

    if find_date_or_not.get() == 1:
        find_date_checkbox_msg.config(text="Date option ON")
        date_format_menu.configure(state="normal")
        entry_sep.configure(state="normal")
        loc_menu.configure(state='normal')
    elif find_date_or_not.get() == 0:
        find_date_checkbox_msg.config(text="Date option OFF")
        date_format_menu.configure(state="disabled")
        entry_sep.configure(state="disabled")
        loc_menu.configure(state="disabled")
        #w.config(state=DISABLED)

    #stanford CoreNLP
    if save_stanford_or_not.get() == 1:
        newPath = stanford_core_NLP_path.get()
        f=open("StanfordNLP-config.txt", "w+")
        f.write(newPath)
        f.close
        save_stanford_checkbox_msg.config(text="Directory saved")
    elif save_stanford_or_not.get() == 0:
        save_stanford_checkbox_msg.config(text="Stanford CoreNLP directory will NOT be saved")

    #save input
    if save_in_or_not.get() == 1:
        newPath = input_file_path.get()
        f=open("input-config.txt", "w+")
        f.write(newPath)
        f.close
        save_in_checkbox_msg.config(text="Directory saved")
    elif save_stanford_or_not.get() == 0:
        save_in_checkbox_msg.config(text="Input corpus directory will NOT be saved")

    #save output
    if save_out_or_not.get() == 1:
        newPath = output_file_path.get()
        f=open("output-config.txt", "w+")
        f.write(newPath)
        f.close
        save_out_checkbox_msg.config(text="Output directory saved")
    elif save_in_or_not.get() == 0:
        save_out_checkbox_msg.config(text="Output directory will NOT be saved")



#w.config(state=DISABLED)

#stanford dir save

save_stanford_or_not = tk.IntVar()
save_stanford_or_not.set(0)

save_stanford_checkbox = tk.Checkbutton(window, text='Save?', variable=save_stanford_or_not, onvalue=1, offvalue=0, command=print_checkboxes)
save_stanford_checkbox.place(x=label_x_cord*2.25, y=basic_y_cord)

save_stanford_checkbox_msg = tk.Label(window, text='Stanford CoreNLP directory will NOT be saved')
save_stanford_checkbox_msg.place(x=label_x_cord*2.4, y=basic_y_cord)

#input dir save

save_in_or_not = tk.IntVar()
save_in_or_not.set(0)

save_in_checkbox = tk.Checkbutton(window, text='Save?', variable=save_in_or_not, onvalue=1, offvalue=0, command=print_checkboxes)
save_in_checkbox.place(x=label_x_cord*2.25, y=basic_y_cord+y_step)

save_in_checkbox_msg = tk.Label(window, text='Input corpus directory will NOT be saved')
save_in_checkbox_msg.place(x=label_x_cord*2.4, y=basic_y_cord+y_step)

#ouput dir save

save_out_or_not = tk.IntVar()
save_out_or_not.set(0)

save_out_checkbox = tk.Checkbutton(window, text='Save?', variable=save_out_or_not, onvalue=1, offvalue=0, command=print_checkboxes)
save_out_checkbox.place(x=label_x_cord*2.25, y=basic_y_cord+y_step*2)

save_out_checkbox_msg = tk.Label(window, text='Output directory will NOT be saved')
save_out_checkbox_msg.place(x=label_x_cord*2.4, y=basic_y_cord+y_step*2)

#memory options
mem_menu_lb = tk.Label(window, text='Memory option ')
mem_menu_lb.place(x=queries_x_cord, y = basic_y_cord+y_step*3)
mem_menu = tk.OptionMenu(window,memory_var,1,2,3,4)
mem_menu.configure(width=10)
mem_menu.place(x=label_x_cord,y=basic_y_cord+y_step*3)

# Sentence Table
compute_sentence = tk.IntVar()
compute_sentence.set(1)

#sentence table option

sentence_table_checkbox_msg = tk.Label(window, text='A Sentence table will be produced')
sentence_table_checkbox_msg.place(x=label_x_cord_wn,y=basic_y_cord+y_step*4)

sentence_table_checkbox = tk.Checkbutton(window, text='Compute Sentence table', variable=compute_sentence, onvalue=1, offvalue=0, command=print_checkboxes)

sentence_table_checkbox.place(x=queries_x_cord, y=basic_y_cord+y_step*4)
sentence_table_checkbox_msg.place(x=label_x_cord,y=basic_y_cord+y_step*4)

#merge option

merge_file_checkbox_msg = tk.Label(window, text='A merged CoNLL table will be produced')
merge_file_checkbox_msg.place(x=label_x_cord_wn,y=basic_y_cord+y_step*5)

merge_file_or_not = tk.IntVar()
merge_file_or_not.set(1)

merge_file_checkbox = tk.Checkbutton(window, text='Merge CoNLL tables', variable=merge_file_or_not, onvalue=1, offvalue=0, command=print_checkboxes)

merge_file_checkbox.place(x=queries_x_cord,y=basic_y_cord+y_step*5)
merge_file_checkbox_msg.place(x=label_x_cord,y=basic_y_cord+y_step*5)


find_date_checkbox_msg = tk.Label(window, text='Date option OFF')
find_date_checkbox_msg.place(x=label_x_cord_wn,y=basic_y_cord+y_step*6)

find_date_or_not = tk.IntVar()
find_date_or_not.set(0)

find_date_checkbox = tk.Checkbutton(window, text='Filename embeds date', variable=find_date_or_not, onvalue=1, offvalue=0, command=print_checkboxes)
find_date_checkbox.place(x=queries_x_cord+15,y=basic_y_cord+y_step*6)
find_date_checkbox_msg.place(x=label_x_cord,y=basic_y_cord+y_step*6)


date_format_lb = tk.Label(window,text='Date format ')
date_format_lb.place(x=queries_x_cord+30,y=basic_y_cord+y_step*7)
date_format_menu = tk.OptionMenu(window, date_format, 'mm-dd-yyyy', 'dd-mm-yyyy','yyyy-mm-dd','yyyy-dd-mm','yyyy-mm','yyyy')

date_format_menu.configure(width=10)
date_format_menu.place(x=label_x_cord, y = basic_y_cord+y_step*7)

if merge_file_or_not.get() == 0:
    find_date_or_not.set(0)

if find_date_or_not.get() == 0:
    date_format_menu.configure(state='disabled')    

entry_sep_lb = tk.Label(window, text='Date character separator ')
entry_sep_lb.place(x=queries_x_cord+30,y = basic_y_cord+y_step*8)
entry_sep = tk.Entry(window, textvariable=separator_var)
entry_sep.configure(width=2)
entry_sep.place(x=label_x_cord,y=basic_y_cord+y_step*8)

if find_date_or_not.get() == 0:
    entry_sep.configure(state='disabled') 

loc_menu_lb = tk.Label(window, text='Date position ')
loc_menu_lb.place(x=queries_x_cord+30,y = basic_y_cord+y_step*9)
loc_menu = tk.OptionMenu(window,date_loc_var,1,2,3,4,5)
loc_menu.configure(width=10)
loc_menu.place(x=label_x_cord,y=basic_y_cord+y_step*9)

if find_date_or_not.get() == 0:
    loc_menu.configure(state='disabled') 


"""

Small HELP Buttons

"""


button_CoreNLP_help = tk.Button(window, text='? HELP', command=CoreNLP_msgbox)

button_CoreNLP_help.place(x=help_button_x_cord,y=basic_y_cord+y_step*0)



button_corpus_help = tk.Button(window, text='? HELP', command=corpus_msgbox)

button_corpus_help.place(x=help_button_x_cord,y=basic_y_cord+y_step*1)



button_output_help = tk.Button(window, text='? HELP', command=output_msgbox)

button_output_help.place(x=help_button_x_cord,y=basic_y_cord+y_step*2)



button_memory_help = tk.Button(window, text='? HELP', command=memory_msgbox)

button_memory_help.place(x=help_button_x_cord,y=basic_y_cord+y_step*3)



button_sentence_table_help = tk.Button(window, text='? HELP', command=sentence_table_msgbox)

button_sentence_table_help.place(x=help_button_x_cord,y=basic_y_cord+y_step*4)



button_merge_help = tk.Button(window, text='? HELP', command=merge_msgbox)

button_merge_help.place(x=help_button_x_cord,y=basic_y_cord+y_step*5)



#ROBY
button_date_in_filename_help = tk.Button(window, text='? HELP', command=date_in_filename_msgbox)

button_date_in_filename_help.place(x=help_button_x_cord,y=basic_y_cord+y_step*6)



button_date_format_help = tk.Button(window, text='? HELP', command=date_format_msgbox)

button_date_format_help.place(x=help_button_x_cord,y=basic_y_cord+y_step*7)


button_date_separator_help = tk.Button(window, text='? HELP', command=date_separator_msgbox)

button_date_separator_help.place(x=help_button_x_cord,y=basic_y_cord+y_step*8)


button_date_position_help = tk.Button(window, text='? HELP', command=date_position_msgbox)

button_date_position_help.place(x=help_button_x_cord,y=basic_y_cord+y_step*9)

"""

MAJOR BUTTONS

"""

#%%

try:
    isCLA = True
    CoreNLPPath = sys.argv[1]
    inputPath = sys.argv[2]
    # if the third argument is a path, then it is output path
    # else it is the specific input file
    is_path = os.path.isdir(sys.argv[3])
    
    if is_path:
        outputPath = sys.argv[3]
        mem = sys.argv[4]
        mergeFiles = sys.argv[5]
        mergeFiles = int(mergeFiles)
        
        if mergeFiles == 1:
            getDate = sys.argv[6]
            getDate = int(getDate)
            
            if getDate == 1:
                separator = sys.argv[7]
                DateFieldLocation = sys.argv[8]
                DateFieldLocation = int(DateFieldLocation)
                DateFormat = str(sys.argv[9])
                RunCoreNLP(CoreNLPPath, inputPath, outputPath,mem,mergeFiles,getDate,separator,DateFieldLocation,DateFormat)
            #merge no date
            else:
                print('Runnning with merge option, but no date option')
                RunCoreNLP(CoreNLPPath, inputPath, outputPath, mem, mergeFiles, getDate)
        #run with no merging
        else:
            print('Running without merge option')
            RunCoreNLP(CoreNLPPath, inputPath, outputPath, mem, mergeFiles)

    else:
        filename = sys.argv[3]
        outputPath = sys.argv[4]
        mem = sys.argv[5]
        mem = int(mem)
        mergeFiles = sys.argv[6]
        mergeFiles = int(mergeFiles)
        if mergeFiles == 1:
            getDate = sys.argv[7]
            getDate = int(getDate)
            if getDate == 1:
                separator = sys.argv[8]
                DateFieldLocation = sys.argv[9]
                DateFieldLocation = int(DateFieldLocation)
                DateFormat = sys.argv[10]
                #DateFormat = str(sys.argv[10])
            else: #throw away definitions so it runs
                getDate = 0
                separator = '_'
                DateFieldLocation = 1
                DateFormat = 'mm-dd-yyyy'
        else:
            mergeFiles = 0
            getDate = 0
            separator = - '_'
            DateFieldLocation = 1
            DateFormat = 'mm-dd-yyyy'
        RunCoreNLP(CoreNLPPath, inputPath, outputPath,mem,mergeFiles,getDate,separator,DateFieldLocation,DateFormat,filename)
    

except Exception as e:
    isCLA = False
    #print ("\nCommand line arguments are empty, incorrect, or out of order, ERROR: "+e.__doc__)
    print ("\nCommand line arguments are empty, incorrect, or out of order")
    print ("\nGraphical User Interface (GUI) will be activated")
    #print(e)
    window.mainloop()
    

#%%

        
