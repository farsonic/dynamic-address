#!/usr/bin/python

#import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

import time
import sys
import re
import netaddr
import fileinput
import hashlib
import shutil
import json   
from pprint import pprint
from jnpr.junos import Device
import getpass
from jnpr.junos import Device
from jnpr.junos.utils.config import Config




feed_location='/var/www/'
temp_location='/var/tmp/'
 

def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def modify_file(file_name,pattern,value=""):
    fh=fileinput.input(file_name,inplace=True)
    for line in fh:
        replacement=line + value
        line=re.sub(pattern,replacement,line)
        sys.stdout.write(line)
    fh.close()

def delete_line(pattern):
   readFile = open(tempFeed,'r')
   lines = readFile.readlines()
   readFile.close()

   writeFile = open(tempFeed,'w') 

   for line in lines:
    if line != pattern+"\n":
     #print "Not found--->" + line
     writeFile.write(line) 

   writeFile.close()
     

def update_manifest(feedname):
   ts = int(time.time())
   print "Modifying total number of objects for  -> " + feedname 
   with open(tempFeed,'r') as feed:
     count = sum(1 for line in feed) - 5
     print "Revised address count of       -> " + str(count) + "\n"
   feed.close()  

   tree = ET.parse(tempManifest)
   root = tree.getroot()

   for feed in root.iter('feed'):
     name = feed.get('name')
     #print name
     if name == str(feedname):
            feed.set('data_ts',str(ts))
	    feed.set('objects',str(count))
   
   tree.write(tempManifest) 


def create_manifest_entry(feedname): 
    ts = str(int(time.time()))
    print "Inserting new feed into manifest file located at " + feed_location

    tree = ET.parse(tempManifest)
    root = tree.getroot()

    category = root.find('category')
    feed = ET.SubElement(category,'feed',dict(data_ts=ts, name=feedname, objects="0", options="", types="ip_addr ip_range", version=feedname))
    data = ET.SubElement(feed,'data')
    url = ET.SubElement(data,'url')
    url.text='/'

    text=(prettify(root))
    cleantext= "".join([s for s in text.strip().splitlines(True) if s.strip()])

    with open(tempManifest,'w') as file: 
      file.write(cleantext)





def copy_feed_to_tempFeed():
    shutil.copyfile(feed,tempFeed)
    readFile = open(tempFeed)
    lines = readFile.readlines()
    readFile.close()
    writeFile = open(tempFeed,'w')
    writeFile.writelines([item for item in lines[:-1]])
    writeFile.close()

def copy_tempFeed_to_feed():
    shutil.copyfile(tempFeed,feed)

def copy_tempManifest_to_Manifest():
    shutil.copyfile(tempManifest,manifest)

def copy_Manifest_to_tempManifest():
    shutil.copyfile(manifest,tempManifest)
 
def create_newFeed(name):
    shutil.copyfile('Feed',name)


def calculate_md5():
    with open(tempFeed) as file:
      data = file.read()
      md5_returned = hashlib.md5(data).hexdigest()
      file.close()
  
    writeFile = open(tempFeed,'a')
    writeFile.write(md5_returned)
    writeFile.close()



if (sys.argv[1]=='add'):
   feed=feed_location + str(sys.argv[2])
   tempFeed=temp_location + str(sys.argv[2])
   manifest=feed_location+'manifest.xml'
   tempManifest=temp_location+'manifest.xml'
   copy_feed_to_tempFeed()
   copy_Manifest_to_tempManifest()
   ip = netaddr.IPNetwork(sys.argv[3])
   feedname = sys.argv[2]
   address = ip.ip
   size = ip.size 
   adj_size = size -1 
   value = ip.value
   print "\nAdding address of              -> " + str(sys.argv[3]) +" (including " + str(adj_size) + " subequent hosts)"

   if adj_size == 0: 
     newentry = '{"1":' + str(value) +'}'
   else: 
     newentry = '{"2":[' + str(value) + ',' + str(adj_size) +']}'
 
   #print newentry
   modify_file(tempFeed,'#add',newentry)
   calculate_md5()
   update_manifest(feedname)
   copy_tempFeed_to_feed()
   copy_tempManifest_to_Manifest()
   

if sys.argv[1]=='del':
   feed=feed_location + str(sys.argv[2])
   tempFeed=temp_location + str(sys.argv[2])
   manifest=feed_location+'manifest.xml'
   tempManifest=temp_location+'manifest.xml'
   copy_feed_to_tempFeed()
   copy_Manifest_to_tempManifest()
   ip = netaddr.IPNetwork(sys.argv[3])
   feedname = sys.argv[2]
   address = ip.ip
   size = ip.size
   adj_size = size -1 
   value = ip.value
   print "\nRemoving address of            -> " + str(sys.argv[3]) +" (including " + str(adj_size) + " subequent hosts)"

   if adj_size == 0:
     oldline = '{"1":' + str(value) +'}'
   else:
     oldline = '{"2":[' + str(value) + ',' + str(adj_size) +']}'
   delete_line(oldline)

   calculate_md5()
   update_manifest(feedname)
   copy_tempFeed_to_feed()
   copy_tempManifest_to_Manifest()


if sys.argv[1]=='list':
   feed=feed_location + str(sys.argv[2])

   pattern_network = '{"(\d+)":\[\d+,\d+\]}'
   pattern_host = '{"(\d+)":\d+}'
   pattern_ip_network = '{"\d+":\[(\d+),\d+]}'
   pattern_ip_host = '{"\d+":(\d+)}'
   pattern_range = '\d+":\[\d+,(\d+)]}'

   with open(feed,'r') as file: 
     lines = file.readlines()
     
   for line in lines:
    host = re.search(pattern_host,line)
    network = re.search(pattern_network,line)
    if host: 
      ip = str(netaddr.IPAddress(re.findall(pattern_ip_host,line)[0]))
      print "Host entry:    " + ip

    elif network: 
      #ip = re.findall(pattern_ip_network,line)[0]
      ip = str(netaddr.IPAddress(re.findall(pattern_ip_network,line)[0]))
      range = re.findall(pattern_range,line)[0]
      print "Network Entry: " + ip + " (+" + range + " hosts)"
    

if sys.argv[1]=='new':
    name = str(sys.argv[2])
    feed=feed_location + str(sys.argv[2])
    manifest=feed_location+'manifest.xml'
    tempManifest=temp_location+'manifest.xml'
    copy_Manifest_to_tempManifest()
    print name
    create_newFeed(feed)
    create_manifest_entry(name)
    copy_tempManifest_to_Manifest()
    #print "Completed, add the following line to your SRX to accept feed:\n set security dynamic-address address-name "+name+ " profile category IPFilter feed "+name 
    username = raw_input("Please enter your SRX Username:")
    password = getpass.getpass()
    srx_list = 'srx-list'
    srxs = open(srx_list,'r') 
    for srx in srxs: 
     print "Logging into SRX "+srx
     login=str(srx) 
     dev = Device(host=login,user=username,password=password)
     dev.open()
     dev.timeout = 300
     cu = Config(dev)
     set_cmd = 'set security dynamic-address address-name '+name+' profile category IPFilter feed '+name
     cu.load(set_cmd, format='set')
     print "Applying changes, please wait...."
     cu.commit()
     dev.close()
     
     
     
     




if sys.argv[1]=='drop':
    name = feed_location + str(sys.argv[2])
    print name
    print "do this next...."


if sys.argv[1]=='setup':
    print "Kick off initial setup process, copy files to target directories etc" 

