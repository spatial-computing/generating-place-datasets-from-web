1) For executing the script make sure you have following python packages installed in system.
-urllib2,re,random,time,os,sys,bs4,datetime,operator,csv,StringIO,gzip,geopy

You can install on ubuntu based systems using PIP as
sudo pip install <package name>

Install pip using
sudo apt-get install pip

2) Configure following two files <Please do not rename these files other wise script will be required to be changed for the same>
    a) input.txt:
        first line containing the city name and following lines containing the street names
        ex:
        Glendale
        S Glendale Ave
        S Brand Blvd
        S Central Ave
        E California Ave
        
    b) place_type.txt:
       Each line in this file corresponds to place types that will be searched in the specified area.
       For enabling a type of area just remove the # from the place type line and similarily for disabling add a # sign in front of place   type    .
       ex:
       #church
       school
       #hospital
       #club
       Script will only search for "school" in the given area for this place_type.txt

3) Run script now using:
    > python googlecrawler.py input.txt 
   Do not run parallel execution of script in same folder if so required duplicate the web_scrapper folder and run it separately.
   
   If any network error encountered re run the script it will resume from last execution step or even kill or stop script it will resume from last execution step.
   For starting a clean start and ignoring old files use -n option as:
   > python googlecrawler.py input.txt -n
   
   For starting a clean start and delete old files use -c option as:
   > python googlecrawler.py input.txt -c
