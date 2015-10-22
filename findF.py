#-*- coding: utf-8 -*-
import urllib2
import re,random,time
import os,sys 
from bs4 import BeautifulSoup,Comment
from datetime import datetime


user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
       'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+',  
       '(KHTML, like Gecko) Element Browser 5.0',  
       'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',   
       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)', 
       'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',   
       'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko)',  
       'Version/6.0 Mobile/10A5355d Safari/8536.25',   
       'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)',   
       'Chrome/28.0.1468.0 Safari/537.36',   
       'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']

def writeFile(f,text):##文本写入文件
    write= open(f,'w')
    write.write(text)
    write.flush()
    write.close()

def OnlyCharNum(s,oth=''):   
    s=s.lower()  
    format='abcdefghijklmnopqrstuvwxyz013456789'
    for c in s:   
        if not c in format:   
            s=s.replace(c,'')
    return s  
    
def modifyText(text):
    count=0
    new_text=[]
    text_mod=[]
    for each_text in list(text):     
        text_mod.append(each_text)       
    for each_text in text_mod:     
        new_text.append(each_text)
        if len(text_mod)-2>count:
            new_text.append(each_text+' '+text_mod[count+1])
            new_text.append(each_text+' '+text_mod[count+1]+' '+text_mod[count+2])
        count=count+1    
    return new_text        
"""
Function to process each tag and extract address from the text
Searching for format in text
Starting with #Street number- a number
contains street name- essentially after street number
contains- key ex: culver city

"""    
def processTags(tags,list1,key,data_flag):
    temp1=re.compile('[0-9]{3,4}')
    flag=0          
    for each_tag in tags:
        line_flag=0 #Extracting textual data from each tag
        if data_flag:
            line_t=each_tag.get_text().strip()
        else:
            line_t=each_tag    
        print "Test:",line_t
        #searching for street number in tag
        if(temp1.search(line_t)!=None):
            start=temp1.search(line_t).span()[0]
            if start !=0: #If text starts with non digit character
                #Trimming all data till the first digit character is found
                if line_t.lower().find(key)>-1:
                    line_flag=1              
                line_temp=line_t        
                line_t=line_t[start:]           
                if(line_t.lower().find(key)<0 and line_flag==1):
                    line_t=line_t+","+key
                    line_flag=0
        if(temp1.search(line_t)!=None):
            line_t=' '.join(re.findall('\w+',line_t))
            if(re.match(r'^\d',line_t) and line_t.lower().find(key)>-1 and line_t.find(",")>-1 and len(line_t)<100):
                if(re.match(r'^\d{4}..+'+key,line_t.lower())):
                    list1.append(line_t)
                    print "Found address:",line_t
                    flag=1
            elif (re.match(r'^\d',line_t) and line_t.lower().find(key)>-1 and line_t.find(",")>-1 and len(line_t)>100):
                #if length constraint is violating removing extra textual data
                s1=temp1.search(line_t).span()[0]
                e1=temp1.search(line_t).span()[1]
                first=line_t[s1:e1]
                line_t_temp=line_t[e1:]
                if(temp1.search(line_t_temp)):
                    s2=temp1.search(line_t_temp).span()[1]
                    second=line_t_temp[:s2]
                    line_t=first+second
                    if(re.match(r'^\d',line_t) and line_t.lower().find(key)>-1 and line_t.find(",")>-1 and len(line_t)<100):
                        print "Found address:",line_t
                        flag=1
                        list1.append(line_t)
            elif (re.match(r'^\d',line_t) and line_t.lower().find(key)>-1 and line_t.find(",")<0 and len(line_t)<100):
                #If comma is missing check for pattern of key followed by CA
                if re.match(r'^\d.*'+key+'.*ca',line_t.lower()):
                    e1=re.match(r'^\d.*'+key+'.*ca',line_t.lower()).span()[1]
                    line_t=line_t[:e1]
                    if (re.match(r'^\d',line_t) and line_t.lower().find(key)>-1 and len(line_t)<100):
                        print "Found address:",line_t
                        flag=1
                        list1.append(line_t)
    return list1,flag               

#Function to open temporary saved html file and find relevant tag through it    
def getAddress(path,key):       
    list1=[]
    html_file= open(path)
    html_data=html_file.read()  
    soup = BeautifulSoup(html_data,'html.parser')
    [s.extract() for s in soup('script')]   #Removing all script tag
    #Find tag address in document       
    if(len(soup.find_all('address'))!=0):
        address=soup.find_all('address')
        for each_address in address:
            list1.append(each_address.get_text())
        print list1         
    else:
        #find all tags with id or class value as address
        if(len(soup.find_all(id='address',class_='address'))!=0):
            #if address found in any of the tag having id or class as address
            address=soup.find_all(id='address',class_='address')
            for each_address in address:
                list1.append(each_address.get_text())
            print "Found address:",each_address.get_text()
        else:
            #Find all p tags
            all_tags=soup.find_all('p')
            print "Processing P tags"
            list1,flag=processTags(all_tags,list1,key,1)      
            #if address is not found in any p tag   
            if flag!=1:
                #find all div tag
                all_div_tags=soup.find_all('div')               
                list1,flag=processTags(all_div_tags,list1,key,1)
                #find all td tags
                all_tags=soup.find_all('td')
                list1,flag1=processTags(all_tags,list1,key,1)
                #find all ul tags
                all_tags=soup.find_all('ul')
                list1,flag2=processTags(all_tags,list1,key,1)
                if flag!=1 and flag1!=1 and flag2!=1:
                    text=soup.stripped_strings
                    text=modifyText(text)
                    list1,flag2=processTags(text,list1,key,0)                                   
    list1=list(set(list1))  #Remove all exact duplicates from found addresses
    html_file.close()                    
    return list1                                                                                    

#Function to take url and fetch html content of it from web
def readAddress(url,output_file,error_log,count_addr,key):
    line=url
    #if url is valid and not from any maps or a pdf document      
    if line.startswith('https://books')==False and (line.startswith('https://maps')==False and line.strip().endswith('.pdf')==False) and line.lower().find('zillow')<0 and line.lower().find('redfin')<0 and  line.lower().find('movoto')<0 and line.lower().find('trulia')<0 and line.lower().find('realtor')<0 and line.find('re/max')<0:                                 
        time.sleep(5)
        try:
            request = urllib2.Request(line)
            length = len(user_agents)
            index = random.randint(0, length-1)
            user_agent = user_agents[index]
            request.add_header('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:40.0) Gecko/20100101 Firefox/40.0')            
            html_doc =urllib2.urlopen(request)
            print "URL fetch sucessfull"
        except Exception as error:
            print "Url fetch Failed !!!"                      
            print "Error encountered:",error
            return count_addr
        soup = BeautifulSoup(html_doc)
        #writing html data in temporary file            
        writeFile("data",str(soup))
        list1=getAddress("data",key)        
        if(len(list1)>0):
            count_addr=count_addr+len(list1)
            print "Addresses:",list1                 
            for ll in list1:    
                #writing data in output file         
                output_file.write(ll.encode('utf-8').strip())
                output_file.write("\n")
        else:
            #keeping track of errors encountered
            error_log.write(line)
            try:
                error_log.write(str(soup))
            except:
                error_log.write("Unable to write string even after encoding")    
            error_log.write('\n')
            print "No Address Found"
            output_file.write("No Address found !!!")
            output_file.write("\n")                     
    return count_addr                                               

#Function to read all found url's and process each one of it
def listFile(url_file,dir_name,key):
    progress_file_name=dir_name+'/current_progress_2.txt'
    if os.path.exists(progress_file_name):
        progress_file=open(progress_file_name,'r')
        lines=progree_file.readlines()        
        if (lines[0].find('2-')>-1 and lines[0].find('complete')>-1):
            return
        else:
            count=lines[0].split('-')[1]
            count_addr=lines[0].split('-')[2]
    else:
        progress_file=open(progress_file_name,'w')
        count=0
        count_addr=0
        progress_file.write('2-'+str(count)+'-'+str(count_addr)+'-')
    progress_file.close()             
    input_file=open(url_file,'r') 
    output_file= open(dir_name+'/all_address.txt','a')
    error_log=open(dir_name+"/error_log.txt",'a') 
    input_lines=input_file.readlines()
    count_url=0    
    for each_line in input_lines:
        output_file.write("\n") 
        output_file.write(each_line)        
        if(each_line[0]!="#" and len(each_line)>5):         
            count_url=count_url+1
            print "Working on url:",each_line
            if count_url>=count:                                                            
                count_addr=readAddress(each_line,output_file,error_log,count_addr,key)   
                print "Address found: ",count_addr," URLS processed: ",count_url                                 
                progress_file=open(progress_file_name,'w')
                progress_file.write('2-'+str(count_url)+'-'+str(count_addr)+'-')
                progress_file.close()                
    output_file.close()
    error_log.close()
    input_file.close()
    progress_file=open(progress_file_name,'w')
    progress_file.write('2-'+str(count_url)+'-'+str(count_addr)+'-complete')     
    progress_file.close()
    
if __name__ == '__main__':
    key=''
    if len(sys.argv)<2:
        print "Usage: findF.py Key ex: findF.py culver city"
    else:
        i=1
        while i<len(sys.argv):
            key=key+sys.argv[i].lower().strip()+' '
            i=i+1
        key=key.strip()    
        dir_name="result_"+datetime.now().strftime('%H%M%S')        
        os.mkdir(dir_name)            
        listFile('_URLS.txt',dir_name,key)    
