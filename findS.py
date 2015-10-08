import urllib
import urllib2
import operator
import re, random,time,os
from bs4 import BeautifulSoup
import csv
import sys
from StringIO import StringIO
import gzip


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
       

def extractUrl(href):
        url = ''
        pattern = re.compile(r'(http[s]?://[^&]+)&', re.U | re.M)
        url_match = pattern.search(href)
        if(url_match and url_match.lastindex > 0):
            url = url_match.group(1)
        return url
        
                       
def getTitle(url):
    print "got:",url
    pos=url.rfind("http")
    url=url[pos:]
    print "passed",url   
    try:
        length = len(user_agents)
        index = random.randint(0, length-1)
        request = urllib2.Request(url)
        request.add_header('User-agent', user_agents[index])        
        request.add_header('referer','www.example.com')
        request.add_header('connection','keep-alive')                     
        response =urllib2.urlopen(request)        
        html = response.read()       
    except Exception as error:
        print "Url fetch Failed !!!"                      
        print "Error encountered:",error
        return url
    soup = BeautifulSoup(html)
    try:
        all_header=soup.findAll("h1")
        i=0
        while all_header[i].text=='' and i<len(all_header): 
            i=i+1
        print "Found title:",all_header[i].text
        return all_header[i].text        
    except:
        print "h1 not found skipping finding h2"
        all_header=soup.findAll("h2")    
        return all_header[0].text
    
           
def getGoogle(address):    
    queryStr = urllib2.quote(address)
    url = 'https://www.google.com/search?hl=en&num=1&q='+queryStr   
    request = urllib2.Request(url)
    index = random.randint(0, 11)  
    sleep_time=random.randint(37, 67)        
    user_agent = user_agents[index]    
    request.add_header('User-agent', user_agent)        
    request.add_header('referer','www.example.com')
    request.add_header('connection','keep-alive')
    print "searching for:",url  
    try:
        response = urllib2.urlopen(request)
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read() 
    except urllib2.URLError, err:
        print "Some other error happened:", err.reason               
    html = response.read()
    soup = BeautifulSoup(html,'html.parser')
    print "Sleeping for:",sleep_time
    time.sleep(sleep_time) 
    for link in soup.findAll("h3",{"class":"r"}):
        url=link.a["href"][7:]       
    link=soup.findAll("h3",{"class":"r"})
    if(len(link)>1):
        url1=link[1].a["href"]
        url1=extractUrl(url1)
        address=urllib2.unquote(url1)
        final_title=getTitle(address)
    else:
        final_title=getTitle(urllib2.unquote(link[0].a["href"]))    
    print "Found Title:",final_title
    return (urllib2.unquote(url),final_title,address)
        
        
def get_address_details(address_file,dir_name):    
    excel_file=open(dir_name+'/all_address.csv','ab')        
    spamwriter = csv.writer(excel_file,dialect='excel')
    spamwriter.writerow(['key','url', 'title', 'address'])
    excel_file.close()
    serial=1;
    input_file=open(address_file,'rb')
    data=input_file.readlines()    
    for each_line in data:
        if len(each_line)>4 and serial>=1:                               
            each_line=each_line.split('USA')[0]+'USA'            
            excel_file=open(dir_name+'/all_address.csv','ab')  
            spamwriter = csv.writer(excel_file,dialect='excel')         
            try:
                (a,b,c)=getGoogle(each_line)                               
                spamwriter.writerow([str(serial),a, b, c])                                      
                print "worked on:",serial                                      
            except :
                sleep_time=random.randint(37, 67)
                time.sleep(sleep_time)
                continue
        serial=serial+1    
    excel_file.close()
    input_file.close()
                    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: findS.py directoryName(containing final_all_address.txt)"
    else:        
        dir_name=sys.argv[1].lower().strip()               
        get_address_details(dir_name+'/final_all_address.txt',dir_name)
