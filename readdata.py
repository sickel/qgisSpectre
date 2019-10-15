#!/usr/bin/python3

# This script can read a csv-file exported from radassist and insert data into a postgis table to be used by the qgisSpectre plugin
# 
# schema.sql creates a appropriate table in a postgis enabled postgresql database
#
# Copyright Morten Sickel, 2019

import sys
import psycopg2

filename=sys.argv[1]

dsn = "dbname=spectredb" # Must be set to be able to connect to database
conn = psycopg2.connect(dsn)
cur=conn.cursor()
insert= "insert into measure (latitude,longitude,altitude,acqtime,flightdosevd1,flightdosevd2,specvd1,specvd2,laseralt,radalt,pressure,temperature,linenumber,filename) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

def lst2pgarr(alist):
    return '{' + ','.join(alist) + '}'

f = open(filename, "r",encoding='latin-1')
header=True
idxs=[]
for idx,line in enumerate(f):
  data=(line.split(',')) 
  if(header):
    if idx ==1:
       # print(data)
        matching = [s for s in data if "Spectrum VD" in s]
        print(matching)
        get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x in y]
        idxs=get_indexes("Spectrum VD",data)
    header = idx<2
  else:
    vd1=lst2pgarr(data[idxs[0]:idxs[0]+1024])
    vd2=lst2pgarr(data[idxs[1]:idxs[1]+1024])
    insdata=[data[9],data[8],data[10],data[1],data[14],data[28],vd1,vd2,data[24],data[23],data[22],data[21],data[11],filename]
    insdata=[x if x !='' else None for x in insdata]
    # print(insdata)
    cur.execute(insert,insdata)

cur.execute("update measure set geom=ST_SetSRID(ST_MakePoint(Longitude, Latitude),4326) where geom is null")
conn.commit()
conn.close()
