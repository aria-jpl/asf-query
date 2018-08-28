#!/usr/bin/env python
from __future__ import print_function

import re
import datetime
import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import qquery.query
import json

'''
This worker queries data products from https://api.daac.asf.alaska.edu and submits them as a download job
'''

# Global constants
url = "https://api.daac.asf.alaska.edu/services/search/param?"
dtreg = re.compile(r'S1[AB].*?_(\d{4})(\d{2})(\d{2})')

class asf(qquery.query.AbstractQuery):
    '''
    ASF query implementer
    '''
    def query(self,start,end,aoi,mapping="S1_IW_SLC"):
        '''
        Performs the actual query, and returns a list of (title, url) tuples
        @param start - start time stamp
        @param end - end time stamp
        @param aoi - area of interest
        @mapping - type of product to queried. defaults to S1_IW_SLC
        @return: list of (title, url) pairs
        '''
        session = requests.session()
        # Build the Query
        if mapping == "S1_IW_SLC":
            qur = self.buildQuery(start,end,'Sentinel-1A,Sentinel-1B',aoi['location']['coordinates'],mapping)
            return self.listAll(session,qur)
        if mapping == "S1_GRD":
            qur = self.buildQuery(start,end,'Sentinel-1A,Sentinel-1B',aoi['location']['coordinates'],mapping)
            return self.listAll(session,qur)

    @staticmethod   
    def getDataDateFromTitle(title):
        '''
        Returns the date typle (YYYY,MM,DD) give the name/title of the product
        @param title - title of the product
        @return: (YYYY,MM,DD) tuple
        '''
        match = dtreg.search(title)
        if match:
            return (match.group(1),match.group(2),match.group(3))
        return ("0000","00","00")

    @staticmethod
    def getFileType():
        '''
        What filetype does this download
        '''
        return "zip"

    @classmethod
    def getSupportedType(clazz):
        '''
        Returns the name of the supported type for queries
        @return: type supported by this class
        '''
        return "asf"    

    # ASF no longer requiring OAuth cookie
    #@classmethod
    #def getOauthUrl(clazz):
    #   '''
    #   Returns the name of the supported oauth type for sling jobs
    #   @return: authentication url if there is an oauth type
    #   '''
    #   return "https://vertex.daac.asf.alaska.edu/services/authentication"
        
    @staticmethod
    def buildQuery(start,end,type,bounds,mapping):
        '''
        Builds a query for the system
        @param start - start time in 
        @param end - end time in "NOW" format
        @param type - type in "slc" format
        @param bounds - bounds to query
        @return query for talking to the system
        '''  
        if mapping=="S1_IW_SLC":
            bounds = bounds[0]
            ply = ",".join([",".join([str(dig) for dig in point]) for point in bounds])
            q=url+"polygon="+ply
            start = datetime.datetime.strftime(datetime.datetime.strptime(start.rstrip('Z'),'%Y-%m-%dT%H:%M:%S%f'), '%Y-%m-%dT%H:%M:%S')+'UTC'
            end = datetime.datetime.strftime(datetime.datetime.strptime(end.rstrip('Z'),'%Y-%m-%dT%H:%M:%S%f'), '%Y-%m-%dT%H:%M:%S') +'UTC'
            q+="&start="+start+"&end="+end
            q+="&platform="+type
            q+='&processingLevel=SLC'
            q+="&output=json"
        elif mapping=="S1_GRD":
            q=url
            start = datetime.datetime.strftime(datetime.datetime.strptime(start.rstrip('Z'),'%Y-%m-%dT%H:%M:%S%f'), '%Y-%m-%dT%H:%M:%S')+'UTC'
            end = datetime.datetime.strftime(datetime.datetime.strptime(end.rstrip('Z'),'%Y-%m-%dT%H:%M:%S%f'), '%Y-%m-%dT%H:%M:%S') +'UTC'
            q+="start="+start+"&end="+end
            q+="&platform="+type
            q+='&processingLevel=GRD_HS,GRD_HD'#,GRD_MS,GRD_MD,GRD_FS,GRD_FD'
            q+="&output=json"
        return q
        
    #Non-required helpers
    @staticmethod
    def listAll(session,query):
        '''
        Lists the server for all products matching a query. 
        NOTE: this function also updates the global JSON querytime persistence file
        @param session - session to use for listing
        @param query - query to use to list products
        @return list of (title,link) tuples
        '''
        print("Listing: "+query)
        response = session.get(query)
        title = None
        found = []
        print(response)
        if response.status_code != 200:
            print("Error: %s\n%s" % (response.status_code,response.text))
            raise qquery.query.QueryBadResponseException("Bad status")
        #parse the granules and download links
        json_data = json.loads(response.text)
        found = []
        for item in json_data[0]:
            title = item['granuleName']
            link = item['downloadUrl']
            found.append((title,link))
        return found
