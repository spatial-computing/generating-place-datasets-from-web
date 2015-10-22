#-*- coding: utf-8 -*-
#
# Create by Meibenjin. 
#
# Last updated: 2013-04-02
#
# google search results crawler 

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import shutil
from urllib import urlopen  
import csv
import urllib2, socket, time
import gzip, StringIO
import re, random, types
from bs4 import BeautifulSoup
from findF import listFile
from findS import get_address_details
from datetime import datetime
from geocode import refine_address


base_url = 'https://www.google.com'
results_per_page = 10
expect_num = 30
key=""
user_agents = list()

    
# results from the search engine
# basically include url, title,content
class SearchResult:
    def __init__(self):
        self.url= '' 
        self.title = '' 
        self.content = '' 

    def getURL(self):
        return self.url

    def setURL(self, url):
        self.url = url 

    def getTitle(self):
        return self.title

    def setTitle(self, title):
        self.title = title

    def getContent(self):
        return self.content

    def setContent(self, content):
        self.content = content

    def printIt(self, prefix = ''):
        print 'ASDFSDVSADF'
        print 'url\t->', self.url
        print 'title\t->', self.title
        print 'content\t->', self.content
        print 

    def writeFile(self, filename):
        file = open(filename, 'a')
        try:
            file.write('url:' + self.url+ '\n')
            file.write('title:' + self.title + '\n')
            file.write('content:' + self.content + '\n\n')
        except IOError, e:
            print 'file error:', e
        finally:
            file.close()



def getName(each_site):    
    pos=each_site.find('www.');
    if pos==-1:
        pos=each_site.find('.');
        each_site=each_site[pos+len('.'):]
    else:
        each_site=each_site[pos+len('www.'):]
    pos_end=each_site.find('.')
    each_site=each_site[:pos_end]
    return each_site
    
    
class GoogleAPI:
    def __init__(self):
        timeout = 50
        socket.setdefaulttimeout(timeout)

    def randomSleep(self):
        sleeptime =  random.randint(37, 67)
        print "Sleeping for :",sleeptime
        time.sleep(sleeptime)

    def writeHtml(self, filename, html):
        file = open(filename, 'a')
        try:
            file.write(html)
        except IOError, e:
            print 'file error:', e
        finally:
            file.close()
    #extract the domain of a url
    def extractDomain(self, url):
        domain = ''
        pattern = re.compile(r'http[s]?://([^/]+)/', re.U | re.M)
        url_match = pattern.search(url)
        if(url_match and url_match.lastindex > 0):
            domain = url_match.group(1)
        return domain

    #extract a url from a link
    def extractUrl(self, href):
        url = ''
        pattern = re.compile(r'(http[s]?://[^&]+)&', re.U | re.M)
        url_match = pattern.search(href)
        if(url_match and url_match.lastindex > 0):
            url = url_match.group(1)
        return url 

    # extract serach results list from downloaded html file
    def extractSearchResults(self, dir_name,html, p, query,flag,invalid_site):
        number=0
        results = list()
        soup = BeautifulSoup(html)
        div = soup.find('div', id  = 'search')
        if (type(div) != types.NoneType):
            lis = div.findAll('li', {'class': 'g'})
            if(len(lis) > 0):
                for li in lis:
                    result = SearchResult()
                    h3 = li.find('h3', {'class': 'r'})
                    if(type(h3) == types.NoneType):
                        continue
                    # extract domain and title from h3 object
                    link = h3.find('a')
                    if (type(link) == types.NoneType):
                        continue
                    url = link['href']
                    url = self.extractUrl(url)
                    if(cmp(url, '') == 0):
                        continue
                    title = link.renderContents()
                    result.setURL(url)
                    try:
                        print 'url:', url
                        address=urllib2.unquote(url)
                        print 'address:', address
                        if(flag):
                            word=getName(address)
                            print "checking for site:",word
                            print "sites to check\n",invalid_site
                            if word not in invalid_site:
                                fileExtract = open(dir_name+'/_URLS.txt', 'a')
                                fileExtract.write(str(address)+'\n')
                                fileExtract.close()
                        number=number+1
                    except Exception, e:
                        print 'error in download:', e
                        self.randomSleep()
                        number=number+1
                        continue
                    result.setTitle(title)
                    span = li.find('span', {'class': 'st'})
                    if (type(span) != types.NoneType):
                        content = span.renderContents()
                        result.setContent(content)
                    results.append(result)
        return results

    # search web
    # @param query -> query key words 
    # @param lang -> language of search results  
    # @param num -> number of search results to return 
    def search(self, query,dir_name,invalid_site, flag,lang='en', num=results_per_page):
        search_results = list()
        squery=query
        query = urllib2.quote(query)
        if(num % results_per_page == 0):
            pages = num / results_per_page
        else:
            pages = num / results_per_page + 1
        for p in range(0, pages):
            start = p * results_per_page 
            url = '%s/search?hl=%s&num=%d&start=%s&q=%s' % (base_url, lang, results_per_page, start, query)
            retry = 2
            while(retry > 0):
                try:
                    request = urllib2.Request(url)
                    length = len(user_agents)
                    index = random.randint(0, length-1)
                    user_agent = user_agents[index]
                    request.add_header('User-agent', user_agent[:-1])
                    request.add_header('Accept-Encoding', 'gzip')
                    request.add_header('referer','www.example.com')
                    request.add_header('connection','keep-alive')
                    response = urllib2.urlopen(request)
                    self.randomSleep() 
                    html = response.read()
                    if(response.headers.get('content-encoding', None) == 'gzip'):
                        print('enter if')
                        html = gzip.GzipFile(fileobj=StringIO.StringIO(html)).read()
                    results = self.extractSearchResults(dir_name,html,p,query,flag,invalid_site)
                    search_results.extend(results)
                    break;
                except urllib2.URLError,e:                   
                    print 'url error:', e                    
                    retry = retry - 1
                    print "Retry value:",retry
                    self.randomSleep()                    
                    continue 
                except Exception, e:
                    print 'error:', e
                    retry = retry - 1
                    self.randomSleep()
                    continue
            if retry<=0:
                break
##        print search_results
        return search_results 

def load_user_agent():
    fp = open('user_agents', 'r')
    line  = fp.readline().strip('\n')
    while(line):
        user_agents.append(line)
        line = fp.readline()
    fp.close()
    
def findInvalidSites(final_site):
    invalid_site=[]
    for each_site in final_site:
        each_site=getName(each_site.getURL())
        #checking if amongst invalid sites any imp site populated adjust if statements accordingly for any other site
        if each_site.lower().find('yelp')<0:
            invalid_site.append(str(each_site))
    print "Invalid site found:",invalid_site
    print "If any relevant site found as invalid then adjust if statements in googlecrawler.py:243"        
    return invalid_site    
    

def crawler(key,dir_name):
    progress_file_name=dir_name+'/current_progress_1.txt'
    if os.path.exists(progress_file_name):
        progress_file=open(progress_file_name,'r')
        lines=progress_file.readlines()        
        if (lines[0].find('1-')>-1 and lines[0].find('complete')>-1):
            return
        else:
            count=lines[0].split('-')[1]
    else:
        progress_file=open(progress_file_name,'w')
        count=0
        progress_file.write('1-'+str(count)+'-') 
    progress_file.close()                   
    invalid_site=[]
    # Load use agent string from file
    load_user_agent()
    # Create a GoogleAPI instance
    api = GoogleAPI()    
    #find_invalid_sites and filter them
    query=key+", rent house"
    results1 = api.search(query,dir_name,invalid_site, 0,num = 3)
    query1=key+", buy house"
    results2 = api.search(query1,dir_name,invalid_site,0, num = 3)
    final_site=results1+results2;
    invalid_site=findInvalidSites(final_site)    
    print "Invalid site names:\n",invalid_site
    if(len(sys.argv) >= 2):
        keywords = open(dir_name+'/keywords_new.txt', 'r')
        keyword = keywords.readline()
        key=keyword.split(',')[1].strip()
        current=0        
        while(keyword):
            if current>=count:
                print "Searching for:",keyword
                fileExtract = open(dir_name+'/_URLS.txt', 'a')
                fileExtract.write("\n"+"##"+str(keyword))
                fileExtract.close()
                results = api.search(keyword,dir_name,invalid_site,1, num = expect_num)
                if len(results)==0:
                    print "url Error"
                    return
                for r in results:
               	    r.printIt()
               	progress_file=open(progress_file_name,'w')    
               	progress_file.write('1-'+str(current)+'-')      
               	progress_file.close()
            keyword = keywords.readline()
            current=current+1
        keywords.close()
        progress_file=open(progress_file_name,'w')
        progress_file.write('1-'+str(current)+'-complete')     
        progress_file.close()

def createKeywordsFile(file_name,dir_name):
    input_file = open(file_name, 'r')
    output_file=open(dir_name+'/keywords_new.txt','w')
    place_file=open('place_type.txt','r')
    place_types=[]    
    for each_line in place_file.readlines():
        if each_line.find('#')<0:
            place_types.append(each_line.replace('\n',''))    
    print "Working for place types:",place_types
    lines=input_file.readlines()
    city_name=lines[0][:-1]
    for each_line in lines[1:]:
        for each_place_type in place_types:
            output_file.write(each_line[:-1]+', '+city_name+', '+each_place_type)
            output_file.write("\n")
    output_file.close()    
    
def cleanPrevious(status_file_name):
    if os.path.exists(status_file_name):
            status_file=open(status_file_name,'r')
            for each_line in status_file.readlines():
                dir_name=each_line
            shutil.rmtree(dir_name)
            status_file.close()
            os.remove(status_file_name)    
    else:
        return

def cleanPrevious2(status_file_name):
    if os.path.exists(status_file_name):            
            os.remove(status_file_name)    
    else:
        return                  

if __name__ == '__main__':
    if len(sys.argv)<2:
        print "Usage: googlecrawler.py <input file name> <-c optional clean flag>\nUse -c to start a clean start"
        print "Input file format: <City name> and on every new line street names"
    else:
        status_file_name = 'status_file.txt'
        if len(sys.argv)==3:
            if sys.argv[2]=='-c':
                print "Clean start"                
                cleanPrevious(status_file_name)
            if sys.argv[2]=='-n':
                print "new start"                
                cleanPrevious2(status_file_name)    
        input_file=sys.argv[1]
        #check status file        
        if os.path.exists(status_file_name):
            status_file=open('status_file.txt','r')
            for each_line in status_file.readlines():
                dir_name=each_line
        else:                 
            dir_name="result_"+datetime.now().strftime('%H%M%S')	    
            os.mkdir(dir_name)
            status_file=open('status_file.txt','w')
            status_file.write(dir_name)
        status_file.close()    
        createKeywordsFile(input_file,dir_name)        
        keywords = open(dir_name+'/keywords_new.txt', 'r')
        keyword = keywords.readline()
        key=keyword.split(',')[1].strip()
        keywords.close()
        key=key.lower()
        print "Found Key:",key    
        file1 = dir_name+'/_URLS.txt'          
        crawler(key,dir_name)        
        listFile(dir_name+'/_URLS.txt',dir_name,key)
        refine_address(dir_name+'/all_address.txt',dir_name,key)
        get_address_details(dir_name+'/final_all_address.txt',dir_name)
        os.remove(status_file_name)   
