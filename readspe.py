#!/usr/bin/python3
"""
 This script can read a directory of spe files and insert the data into a postgis table to be used by the qgisSpectre plugin

 schema.sql creates a appropriate table in a postgis enabled postgresql database

 Copyright Morten Sickel, 2019
"""


import sys
import psycopg2
import os

if len(sys.argv)==1:
    print("Reading a directory of spe files to upload the data in a postgis database")
    print()
    print("Usage :")
    print(sys.argv[0]+" directory mission")
    print()
    print("If mission is omitted, it defaults to the directory name")
    sys.exit(1)
          
dirname=sys.argv[1]

if len(sys.argv)==2:
    mission=dirname
else:
    mission=sys.argv[2]
height=1
dsn = "dbname=ositest" # Must be set to be able to connect to database
conn = psycopg2.connect(dsn)
cur=conn.cursor()
insert= "insert into measure (latitude,longitude,altitude,acqtime,flightdosevd1,flightdosevd2,specvd1,specvd2,laseralt,radalt,pressure,temperature,linenumber,filename,mission) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

def lst2pgarr(alist):
    return '{' + ','.join(alist) + '}'
Null=None
files=os.listdir(dirname)
files.sort()
for filename in files:
    if filename.endswith("spe"):
        f = open(dirname+"/"+filename, "r",encoding='latin-1')
        header=None
        idxs=[]
        dataset={}
        for idx,line in enumerate(f):
            if(line.startswith("$")):
                header=line[1:]
                header=header[:-2]
                dataset[header]=[]
                
            else:
                line=line[:-1].strip(' ')
                if "= " in line:
                    (k,v)=line.split("= ")
                    if type(dataset[header]) is list:
                        dataset[header]=dict()
                    dataset[header][k]=v
                else:
                    dataset[header].append(line)
                
        vd1=lst2pgarr(dataset['DATA'][1:])
        timing=dataset['MEAS_TIM'][0].split(' ')
        dataset['MEAS_TIM']=timing[1]
        insdata=[dataset['GPS']['Lat'],dataset['GPS']['Lon'],dataset['GPS']['Alt'],dataset['MEAS_TIM'],dataset['DOSE_RATE'][0],Null ,vd1,Null,height,height,Null,dataset['TEMPERATURE'][0],Null,filename,mission]    
        cur.execute(insert,insdata)

cur.execute("update measure set geom=ST_SetSRID(ST_MakePoint(Longitude, Latitude),4326) where geom is null")
conn.commit()
conn.close()
