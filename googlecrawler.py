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
from robobrowser.browser import RoboBrowser
from robobrowser import exceptions
from datetime import datetime
from geocode import refine_address


base_url = 'https://www.google.com.hk'
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
    def extractSearchResults(self, html, p, query,flag,invalid_site):
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
                                fileExtract = open('_URLS.txt', 'a')
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
    def search(self, query,invalid_site, flag,lang='en', num=results_per_page):
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
                    results = self.extractSearchResults(html,p,query,flag,invalid_site)
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
        invalid_site.append(str(each_site))
    return invalid_site    
    

def crawler(key):
    invalid_site=[]
    # Load use agent string from file
    load_user_agent()
    # Create a GoogleAPI instance
    api = GoogleAPI()    
    #find_invalid_sites and filter them
    query=key+", rent house"
    results1 = api.search(query,invalid_site, 0,num = 3)
    query1=key+", buy house"
    results2 = api.search(query1,invalid_site,0, num = 3)
    final_site=results1+results2;
    invalid_site=findInvalidSites(final_site)    
    print "Invalid site names:\n",invalid_site
    if(len(sys.argv) < 2):
        keywords = open('newkeywords', 'r')
        keyword = keywords.readline()
        key=keyword.split(',')[1].strip()        
        while(keyword):
            print "Searching for:",keyword
            fileExtract = open('_URLS.txt', 'a')
            fileExtract.write("##"+str(keyword)+"\n")
            fileExtract.close()
            results = api.search(keyword,invalid_site,1, num = expect_num)
            if len(results)==0:
                print "url Error"
                return
            for r in results:
           	    r.printIt()
            keyword = keywords.readline()
        keywords.close()
    else:
        keyword = sys.argv[1]
        results = api.search(keyword,1, num = expect_num)
        for r in results:
           r.printIt()
                                   

if __name__ == '__main__':
    keywords = open('newkeywords', 'r')
    keyword = keywords.readline()
    key=keyword.split(',')[1].strip()
    keywords.close()
    key=key.lower()
    print "Found Key:",key
    file1 = '_URLS.txt'
    if os.path.exists(file1):
        os.remove(file1)    
    crawler(key)
    dir_name="result_"+datetime.now().strftime('%H%M%S')	    
    os.mkdir(dir_name)
    #dir_name="result_230519"
    listFile('_URLS.txt',dir_name,key)
    refine_address(dir_name+'/all_address.txt',dir_name,key)
    get_address_details(dir_name+'/final_all_address.txt',dir_name)	
    

