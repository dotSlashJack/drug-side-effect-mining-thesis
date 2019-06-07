"""
@author: Jack Hester
Created December 2019
Modified January 2019
Written for "Mining Adverse Drug Effects from Online Healthcare Forum Posts"
Contact jack.hester@emory.edu
Downloads forum posts for analysis
Uses drugs.com forum (see input text files)
Downloading and use of this data was approved by the Emory IRB committee
"""
#import datetime as dt
import requests
import time
from bs4 import BeautifulSoup as bs
import os.path
#import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

oldDrugsFile = open("old-drug-list.txt", "r")
drugs = oldDrugsFile.read().split(',')
oldDrugsFile.close()

newDrugsFile = open("new-drug-list.txt", "r")
newDrugs = newDrugsFile.read().split(',')
newDrugsFile.close()
newDrugs = ['Tymlos','Xermelo']

oldUrlFile = open("drugscom-urls-old.txt", "r")
pages = oldUrlFile.read().split(',')
oldUrlFile.close()

newUrlFile = open("drugscom-urls-new.txt", "r")
newPages = newUrlFile.read().split(',')
newUrlFile.close()
newPages = ['https://www.drugs.com/comments/abaloparatide/tymlos.html'
            ,'https://www.drugs.com/comments/telotristat/xermelo.html']


def getAllPages(url):
    #print(url+" has the following number of "+str(len(urls)))
    listOfPages = []
    listOfPages.append(url)
    for pageNumber in range(2,101): # have a total of up to 100 pages (including 1st page at index 0)
        listOfPages.append(url+'?page='+str(pageNumber))
    return listOfPages

def cleanDate(dateString):
    dateString = dateString.replace('January','01')
    dateString = dateString.replace('February','02')
    dateString = dateString.replace('March','03')
    dateString = dateString.replace('April','04')
    dateString = dateString.replace('May','05')
    dateString = dateString.replace('June','06')
    dateString = dateString.replace('July','07')
    dateString = dateString.replace('August','08')
    dateString = dateString.replace('September','09')
    dateString = dateString.replace('October','10')
    dateString = dateString.replace('November','11')
    dateString = dateString.replace('December','12')
    dateString = dateString.replace(' ','-')
    dateString = dateString.replace(',','')
    return dateString
    
def download(url, drugName):
    #numRevs = 0
    urls = getAllPages(url)
    for i in range(0, len(urls)):
        page = requests.get(urls[i])
        #prevent server overload
        if(i>3 and i%10==0):
            print('paused')
            time.sleep(3) #pause for 10s
            print('resumed')
        #check if page is valid
        #print(urls[i])
        if page.status_code == 200:
             soup = bs(page.text, 'html.parser')
             #get all divs that contain the reviews on that page
             blocks = soup.find_all(class_='boxList')
             for b in blocks:
                 paras = b.find_all('span')
                 body = paras[0].text
                 #para2 = b.find_all('p')[1]
                 #para2Span = b.find_all('span')
                 if len(paras)==6:
                     takenSince = paras[3].text
                     date = paras[4].text
                 elif len(paras) ==5:
                     takenSince = 'no duration available'
                     date = paras[3].text
                 elif len(paras) ==4:
                     takenSince = 'no duration available'
                     date = paras[2].text
                 else:
                     takenSince = 'no duration available'
                     date = 'no date available'
                 #print(body)
                 #save_path = '/Users/jhester/Desktop/thesis-code/drugscom-older-out'
                 #save_path = '/Users/jhester/Desktop/thesis-code/drugscom-newer-out/'
                 if date!='no date available':
                     date = cleanDate(date)
                 titleStr = drugName+'_'+date
                 titleStr = titleStr.replace('?','')
                 titleFull = save_path+titleStr
                 # prevent overwrite of files w/same date by adding index to end of name
                 index = 0
                 while os.path.isfile(titleFull+'.txt') and index<20:
                     index = index+1
                     temp = titleFull.split('_n')[0]
                     newf = temp+'_n'+str(index)
                     #print(newf)
                     if index == 1:
                         #temp = titleFull.split('.txt')
                         nmin1 = titleFull+'.txt'
                     else:
                         nmin1 = temp+'_n'+str(index-1)+'.txt'
                     with open(nmin1) as myfile:
                         if body in myfile.read():
                             myfile.close()
                             titleFull = nmin1.split('.txt')[0]
                             index = 20
                         else:
                             titleFull = newf
                 titleFull = titleFull+'.txt'
                 
                 # write the review to a file
                 f = open(titleFull,'w+')
                 #print(body)
                 f.write(body)
                 f.write('\n\n')
                 #print('date: '+date)
                 f.write(takenSince+'\n')
                 f.close()
                 #numRevs = numRevs+1
        else:
            index = 0
            return
            #print('found all valid links')
            #break
            #return
        

"""for p in range(0, len(pages)):
    print('downloading old drugs')
    download(pages[p], drugs[p])
"""
"""
for n in range(0, len(newPages)):
    print('downloading new drugs')
    download(newPages[n], newDrugs[n])
"""
