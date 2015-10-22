from geopy.geocoders import GoogleV3
from geopy.geocoders import Nominatim
from geopy.geocoders import Bing
from geopy.geocoders import OpenMapQuest
import re
import os,sys
import time

geolocator1 = Nominatim()
geolocator2 = GoogleV3()
geolocator3 = OpenMapQuest()

def find_location1(each_line):
    """
        uses vaious geocoding services provided by python library geopy.
        if information not found by first service try and fetch from other services.
    """    
    try:
        location=geolocator2.geocode(each_line)                
    except:
        try:
            location=geolocator1.geocode(each_line)      
        except:
            try:
                location=geolocator3.geocode(each_line)               
            except:
                return None 
    return location            

def find_location(each_line):
    """
        uses vaious geocoding services provided by python library geopy.
        if information not found by first service try and fetch from other services.
    """    
    try:
        location=geolocator2.geocode(each_line)
        print location.address
        return location
    except:
        try:
            location=geolocator1.geocode(each_line)
            print(location.address)
            return location
        except:
            try:
                location=geolocator3.geocode(each_line)
                print(location.address)
                return location
            except:
                return None  
                  
def refine_address(address_file,dir_name,city):
    """
        Takes input as file generated using findF.py which contains raw addresses.
        Geocoding each address and trying to find more specific address and geocoded information
        Ouput written in file final_all_address.txt
    """
    progress_file_name=dir_name+'/current_progress_3.txt'
    if os.path.exists(progress_file_name):
        progress_file=open(progress_file_name,'r')
        lines=progress_file.readlines()        
        if (lines[0].find('3-')>-1 and lines[0].find('complete')>-1):
            return
        else:
            addr_count=int(lines[0].split('-')[1])
            url_count=int(lines[0].split('-')[2])
            write_count=int(lines[0].split('-')[3])
    else:
        progress_file=open(progress_file_name,'w')
        addr_count=0
        url_count=0
        write_count=0
        progress_file.write('3-'+str(addr_count)+'-'+str(url_count)+'-'+str(write_count)+'-')
    progress_file.close()    
    count=0
    count1=0    
    temp1=re.compile('\d+')
    of_name=dir_name+'/final_all_address.txt'
    outputfile=open(dir_name+'/final_all_address.txt','a')
    check={}
    try:
        check_file=open(dir_name+'/check_file_address.txt','r')        
        lines=check_file.readlines()
        for each_line in lines:
            check[each_line]=1
        check_file.close()        
    except:
        check_file=open(dir_name+'/check_file_address.txt','a')    
    #setting up check file to fetch results from old execution if current execution was interrupted.    
    check_file=open(dir_name+'/check_file_address.txt','a')    
    road_names={'way': 1,'in': 1,'states': 1, 'av': 1, 'blvd': 1, 'ave': 1, 'st': 1, 'dr': 1, '2': 1, 'city': 1, 'lane': 1,'boulevard': 1,'center': 1,'avenue': 1,'valley': 1,'pkwy': 1,'place': 1,'parkway': 1,'main': 1,'pl': 1,'ste':1,'bl':1}
    geolocator = Nominatim()
    with open(address_file,'rb') as input_file:
        for each_line in input_file:           
            if each_line[:2]=="##":
                place_type=each_line.split(',')[2]
            if each_line[0]=='h':
                url_count=url_count+1                
            #process on addresses not other information in file
            if(each_line[0]!="#" and each_line[0]!="h" and len(each_line)>3 and each_line[0]!="N" and each_line.lower().find(city)>-1):
                count1=count1+1
                each_line=' '.join(re.findall('\w+',each_line))
                each_line=each_line.lower()
                print "Processing line",each_line
                #if line is not starting by digit- seek till first digit is encountered
                if not each_line[0].isdigit():
                    if(temp1.search(each_line)):
                        start=temp1.search(each_line).span()[0]
                        each_line=each_line[start:]  
                    else:
                        continue                                       
                print "count:",count1
                #print "learned:",road_names
                #checking for valid address having city name and 4 individual parts in string (street number, street name, city name , CA or zipcode)
                if count1>=addr_count and each_line.lower().find(city)>-1 and len(each_line.split(' '))>4:
                    pos=each_line.lower().find(city)
                    if each_line[pos-1] !=' ' and each_line[pos-1] !=',':
                        each_line=each_line.replace(city,', '+city)                                                            
                    if each_line.lower().rfind('ca')>-1:
                        pos=each_line.lower().rfind(' ca')                        
                        each_line=each_line[:pos]
                    if len(each_line.split(' '))>3 and each_line.find(each_line.split(' ')[3]) != each_line.find(city) and each_line.find(each_line.split(' ')[2]) != each_line.find(city):
                        t=each_line.split(' ')
                        #create a well formed string for geocoding
                        address=''+t[0]
                        address=address+' '+t[1]
                        address=address+' '+t[2]
                        address=address+' '+city 
                        each_line=address
                    print "Attempt 1 now: ",each_line                                 
                    try: 
                        time.sleep(2)                           
                        #try and find geocoded information
                        location = find_location1(each_line)                        
                    except:
                        #not able to geocode refine string more
                        print 'Network error try again'                          
                        print each_line
                    try:
                        print(location.address)
                        road_names[each_line.lower().split(' ')[2]]=1
                    except:
                        print "First attempt failed trying again- refine address"
                        t=each_line.split(' ')
                        address=''+t[0]
                        address=address+' '+t[1]
                        address=address+' '+t[2]
                        count=3
                        print t[2].lower()
                        print road_names
                        if t[2].lower() not in road_names and count1 >0:
                            while count<len(t):
                                address=address+' '+t[count]
                                if t[count].lower() in road_names:
                                    break
                                count=count+1
                        while count<len(t):                           
                            if (t[count].lower().find(city)>-1):                       
                                break                           
                            count=count+1     
                        while count<len(t):
                            address=address+' '+t[count]     
                            count=count+1                         
                        if address.find(city)<0:
                            address=address+', '+city;
                        print "Attempt 2 now: ",address                                                                 
                        try:
                            time.sleep(2) 
                            location = find_location1(address)                            
                        except: 
                            print 'Network error try again'                                                     
                        try:
                            print(location.address)                            
                        except:
                            print "Second attempt failed trying again- refine address"
                            pos=address.lower().find(city)
                            address=address[:pos+len(city)]
                            print "Attempt 3 now: ",address
                            try:
                                time.sleep(2) 
                                location = find_location(address)                                                           
                            except:   
                                print 'Network error'                                                           
                            try:
                                print(location.address)
                            except:
                                print "Third attempt failed skipping- check:",address
                                continue
                    key= str(location.latitude)+str(location.longitude)
                    #get longitude latitude information                            
                    if key not in check and str(location.address).lower().find('ca')>-1 and str(location.address).lower().find(city)>-1:            
                        #if new address found write in final file
                        check[key]=1
                        check_file.write(key);
                        check_file.write('\n');
                        print "Found data:",location.address+' *-* '+str(location.latitude)+' *-* '+str(location.longitude)+' *-* '+place_type
                        try:
                            outputfile.write(location.address+' *-* '+str(location.latitude)+' *-* '+str(location.longitude)+' *-* '+place_type)
                            write_count=write_count+1
                        except:
                            continue
                    else:
                        print "Repeated or Invalid Data: ",location.address
                    progress_file=open(progress_file_name,'w')    
                    progress_file.write('3-'+str(count1)+'-'+str(url_count)+'-'+str(write_count)+'-')
                    progress_file.close()                   
    print "Total url processed:",url_count
    print "Total addresses found:",write_count
    progress_file=open(progress_file_name,'w') 
    progress_file.write('3-'+str(count1)+'-'+str(url_count)+'-'+str(write_count)+'-complete')                                             
    outputfile.close()  
    input_file.close()
    check_file.close()
    progress_file.close()                                                 

if __name__ == '__main__':
    key=''
    if len(sys.argv) < 3:
        print "Usage: geocode.py directoryName(containing all_address.txt) key"
    else:
        i=2
        while i<len(sys.argv):
            key=key+sys.argv[i].lower().strip()+' '
            i=i+1
        key=key.strip()        
        dir_name=sys.argv[1].lower().strip()
        #geocoding the previously found addresses               
        refine_address(dir_name+'/all_address.txt',dir_name,key)
