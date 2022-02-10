# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 10:24:57 2022

@author: Lucas R. Amaral

Course IBM Python Project for Data Engineering
Peer-graded Assignment: Peer Review Assignment
"""

#%clear
import os
import glob
import pandas as pd
from datetime import datetime

#==============================================================================
# It sets the working directory.
#==============================================================================
WORKING_DIRECTORY = """C:\\"""
os.chdir(WORKING_DIRECTORY)
os.getcwd()

#==============================================================================
# It downloads messages to log file.
#==============================================================================
def log(message, logfile = 'logfile.txt'):

    # all event logs will be stored in this "logfile"
                 
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second
    now = datetime.now()                   # get current timestamp
    timestamp = now.strftime(timestamp_format)
    message = timestamp + '\t' + message + '\n'
    with open(logfile, 'a') as f:
        print(message)
        f.write(message)

#==============================================================================
# It downloads json files from urls and saves it to local disk.
# 1. Chicago Socioeconomic Indicators
# This dataset contains a selection of six socioeconomic indicators of public 
# health significance and a hardship index, by Chicago community area, for the
# years 2008 – 2012.
#    
# 2. Chicago Public Schools
# This dataset shows all school level performance data used to create CPS 
# School Report Cards for the 2011-2012 school year.
#
# 3. Chicago Crime Data
# This dataset reflects reported incidents of crime (with the exception of 
# murders where data exists for each victim) that occurred in the City of 
# Chicago from 2001 to present, minus the most recent seven days.
#==============================================================================
file_names = ['data_01_chicago_socioeconomic_indicators.json'
              , 'data_02_chicago_public_schools.json'
              , 'data_03_chicago_crime_data.json']

file_url = ['https://data.cityofchicago.org/resource/kn9c-c2s2.json'
            , 'https://data.cityofchicago.org/resource/9xs2-f89t.json'
            , 'https://data.cityofchicago.org/resource/crimes.json']

#------------------------------------------------------------------------------
def download_json():

    for i, f in enumerate(file_url):
        
        #file_name = f.split('/')
        #file_name = file_name[len(file_name)-1]
        
        file_name = file_names[i]
        log('Downloading file ' + file_name)
   
        df = pd.read_json(f)
        df.to_json(file_name)
       
    return(0)
       
#------------------------------------------------------------------------------
def download():
    download_json()
    return(0)

#==============================================================================
# It extracts data from files.
#==============================================================================
def extract():
   
    #list of data files extracted.
    extracted_data_jsonfile = []
   
    #process all json files
    for jsonfile in glob.glob('*chicago*.json'):
        log('Extracting data from file ' + jsonfile)        
        extracted_data_jsonfile_temp = pd.read_json(jsonfile)
        extracted_data_jsonfile      = extracted_data_jsonfile + [extracted_data_jsonfile_temp]

    return(extracted_data_jsonfile)        


#==============================================================================
# It transforms data.
#==============================================================================

#------------------------------------------------------------------------------
def transform(extracted_data_jsonfile):
    df_indicator = extracted_data_jsonfile[0]
    df_school    = extracted_data_jsonfile[1]
    df_crime     = extracted_data_jsonfile[2]

    df_indicator = df_indicator.applymap(str)
    df_school    = df_school.applymap(str)
    df_crime     = df_crime.applymap(str)

    df_indicator[['percent_of_housing_crowded']]                  = df_indicator[['percent_of_housing_crowded']].applymap(float)
    df_indicator[['percent_households_below_poverty']]            = df_indicator[['percent_households_below_poverty']].applymap(float)
    df_indicator[['percent_aged_16_unemployed']]                  = df_indicator[['percent_aged_16_unemployed']].applymap(float)
    df_indicator[['percent_aged_25_without_high_school_diploma']] = df_indicator[['percent_aged_25_without_high_school_diploma']].applymap(float)
    df_indicator[['percent_aged_under_18_or_over_64']]            = df_indicator[['percent_aged_under_18_or_over_64']].applymap(float)
    df_indicator[['per_capita_income_']]                          = df_indicator[['per_capita_income_']].applymap(float)
    df_indicator[['hardship_index']]                              = df_indicator[['hardship_index']].applymap(float)
    
    df_school[['safety_score']] = df_school[['safety_score']].applymap(float)    
  
    return(df_indicator, df_school, df_crime)
   
#==============================================================================
# It loads data.
#==============================================================================
def load(df):
    file_name = 'load.csv'
    df.to_csv(file_name, index=False)

#==============================================================================
# ETL Process.
#==============================================================================
# Download
log('Downloading files...')
download()
log('Files downloaded succesfully...')

# Extract
log('Extracting data from files...')
extracted_data_jsonfile = extract()
log('Data extracted from files succesfully...')

# Transform
log('Transforming data...')
df_indicator, df_school, df_crime = transform(extracted_data_jsonfile)
log('Data transformed succesfully...')

#==============================================================================
# QUESTIONS
#==============================================================================
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals())

#------------------------------------------------------------------------------
# Problem 1: Find the total number of crimes recorded in the CRIME table.
#------------------------------------------------------------------------------
t  = '\nProblem 1: Find the total number of crimes recorded in the CRIME table.'
st = '''\n
select count(1) as qt_crime
from   df_crime;
'''
r = pysqldf(st)

log(80*'=' + t + '\nSQL: ' + st + '\nTotal numbers in the CRIME table is: ' + str(int(r['qt_crime'])) + '\n'
    , logfile='p1.txt')

#------------------------------------------------------------------------------
# Problem 2: List community areas with per capita income less than 11000.
#------------------------------------------------------------------------------
t  = '\nProblem 2: List community areas with per capita income less than 11000.'
st = '''\n
select ca
   ,   community_area_name
from   df_indicator
where  per_capita_income_ < 11000;
'''
r = pysqldf(st)
r = str((r))

log(80*'=' + t + '\nSQL: ' + st + '\nCommunity areas with per capita income less than 11000:\n ' + r + '\n'
        , logfile='p2.txt')

#------------------------------------------------------------------------------
#Problem 3: List all case numbers for crimes  involving minors (children are 
# not considered minors for the purposes of crime analysis).
#------------------------------------------------------------------------------
t  = '''\nProblem 3: List all case numbers for crimes involving minors(children are 
# not considered minors for the purposes of crime analysis)'''

st = '''\n
select case_number
   ,   primary_type
   ,   description
from   df_crime
where  description like '%MINOR%';
'''
r = pysqldf(st)
r

r = str((r))

log(80*'=' + t + '\nSQL: ' + st + '\nCase numbers for crimes involving minors:\n ' + r + '\n'
        , logfile='p3.txt')


#------------------------------------------------------------------------------
#Problem 4: List all kidnapping crimes involving a child.
#------------------------------------------------------------------------------
t  = '''\nProblem 4: List all kidnapping crimes involving a child.'''

st = '''\n
select case_number
   ,   primary_type
   ,   description
from   df_crime
where  description like '%CHILD%';
'''
r = pysqldf(st)
r
r = str((r))

log(80*'=' + t + '\nSQL: ' + st + '\nThere were not any kidnapping crimes involving a child:\n ' + r + '\n'
        , logfile='p4.txt')
    

#------------------------------------------------------------------------------
#Problem 5: What kind of crimes were recorded at schools.
#------------------------------------------------------------------------------
t  = '''\nProblem 5: What kind of crimes were recorded at schools.'''

st = '''\n
select   t1.primary_type
   ,     count(distinct case_number) as qt_crime_at_school
from     df_crime  t1
join     df_school t2 on t1.community_area = t2.community_area_number
group by t1.primary_type
order by qt_crime_at_school desc;
'''
r = pysqldf(st)
r

r = str((r))

log(80*'=' + t + '\nSQL: ' + st + '\nType and quantity of crimes recorded at schools:\n ' + r + '\n'
        , logfile='p5.txt')
   

#------------------------------------------------------------------------------
#Problem 6: List the average safety score for all types of schools.
#------------------------------------------------------------------------------
t  = '''\nProblem 6: List the average safety score for all types of schools.'''

st = '''\n
select   avg(safety_score) as avg_safety_score
from     df_school;
'''
r = pysqldf(st)
r

r = str((r))

log(80*'=' + t + '\nSQL: ' + st + '\nAverage safety score for all types of schools:\n ' + r + '\n'
        , logfile='p6.txt')


#------------------------------------------------------------------------------
#Problem 7: List 5 community areas with highest % of households below poverty 
# line.
#------------------------------------------------------------------------------
t  = '''\nProblem 7: List 5 community areas with highest % of households below poverty.'''

st = '''\n
select   community_area_name
    ,    percent_households_below_poverty
from     df_indicator
order by percent_households_below_poverty desc
limit 5;
'''
r = pysqldf(st)
r

r = str((r))

log(80*'=' + t + '\nSQL: ' + st + '\nTop 5 community areas with highest % of households below poverty:\n ' + r + '\n'
        , logfile='p7.txt')

#------------------------------------------------------------------------------
#Problem 8: Which community area(number) is most crime prone.
#------------------------------------------------------------------------------
t  = '''\nProblem 8: Which community area(number) is most crime prone.'''

st = '''\n
select    t1.community_area
   ,      count(distinct case_number) as qt_crime
from      df_crime     t1
group by  t1.community_area
order by  qt_crime desc
limit 1;
'''
r = pysqldf(st)
r

log(80*'=' + t + '\nSQL: ' + st + '\nCommunity area(number) is most crime prone: ' + str(r['community_area'][0]) + '\n'
        , logfile='p8.txt')

#------------------------------------------------------------------------------
#Problem 9: Use a sub-query to find the name of the community area with highest
# hardship index.
#------------------------------------------------------------------------------
t  = '''\nProblem 9: Use a sub-query to find the name of the community area with highest hardship index.'''

st = '''\n
select   t1.community_area_name
   ,     t1.hardship_index
from     df_indicator t1
where    t1.hardship_index = (
            select    max(t2.hardship_index)
            from      df_indicator t2
         );    
'''

r = pysqldf(st)
r

log(80*'=' + t + '\nSQL: ' + st + '\nName of the community area with highest hardship index: ' + str(r['community_area_name'][0]) + '(' + str(r['hardship_index'][0]) + ')' + '\n'
        , logfile='p9.txt')


#------------------------------------------------------------------------------
#Problem 10: Use a sub-query to determine the Community Area Name with most 
# number of crimes
#------------------------------------------------------------------------------
t  = '''\nProblem 10: Use a sub-query to determine the Community Area Name with most number of crimes'''

st = '''\n
select    cast(t1.ca as integer) as community_area_code
   ,      t1.community_area_name
   ,      count(distinct case_number) as qt_crime
from      df_indicator     t1
left join df_crime         t2 on cast(t1.ca as integer) = t2.community_area
where     t1.ca not in ('nan')
group by  community_area_code
   ,      t1.community_area_name
order by  qt_crime desc
;    
'''

r = pysqldf(st)
r

log(80*'=' + t + '\nSQL: ' + st + '\nCommunity Area Name with most number of crimes: ' + str(r['community_area_name'][0]) + '(' + str(r['qt_crime'][0]) + ')' + '\n'
        , logfile='p10.txt')


