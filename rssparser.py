#
# Download latest RSS news regarding smart homes
#
import feedparser
import dateutil.parser
from datetime import datetime, date, timedelta
import pyshorteners
import re
import random
import pandas as pd
import os.path
from pathlib import Path
from os import path
import ssl 

ssl._create_default_https_context = ssl._create_unverified_context

_filename = 'latest_news.csv'
_number_of_records = 5
_my_date_pattern = re.compile(
    r'(\d{,2})/(\d{,2})/(\d{4}) (\d{,2}):(\d{2}):(\d{2})')

def myDateHandler(aDateString):
    month, day, year, hour, minute, second = \
        _my_date_pattern.search(aDateString).groups()
    return (int(year), int(month), int(day), \
        int(hour), int(minute), int(second), 0, 0, 0)

def download_websites(n_records, b_yesterday=False):
    urls = ['https://www.cnet.com/rss/smart-home',
            'https://www.pocket-lint.com/rss/smart-home/all.xml',
            'https://news.google.com/rss/search?q=smart+home&hl=en-US&gl=US&ceid=US:en'
        ]

    feedparser.registerDateHandler(myDateHandler)
    feeds = [feedparser.parse(url) for url in urls]
    type_tiny = pyshorteners.Shortener()

    data=[]
    df = pd.DataFrame(data)
    b_record_found = False
    idx_num = 0

    for feed in feeds:
        if feed:
            if (len(feed.entries) > 0): 
                for i in range(n_records):
                    the_date = feed.entries[i].published[5:7] + " " + feed.entries[i].published[8:16]
                    date_object = datetime.strptime(the_date,'%d %b %Y').date()

                    # Download yesterday's feeds
                    if (b_yesterday):
                        if date_object == datetime.today().date() - timedelta(days=1):
                            b_record_found = True
                            #print("Yesterday!")

                    # Download today's feeds                            
                    if date_object == datetime.today().date():
                        b_record_found = True
                        #print("Today!")

                    if b_record_found == True:
                        new_row =  {'idx':idx_num,
                                    'title':feed.entries[i].title, 
                                    'url':feed.entries[i].link, 
                                    'shorturl':type_tiny.tinyurl.short(feed.entries[i].link),
                                    'date':date_object,
                                    'used':'0',
                                    'priority':'0'}
                        #append row to the dataframe
                        df = pd.concat([df, pd.DataFrame.from_records([new_row])])
                        idx_num+=1

                    b_record_found = False    
    return df

def store_records(df, filename):
    with open(filename, "w") as f:        
        df.to_csv(filename, columns=['idx','title','url','shorturl','date','used','priority'], encoding='utf-8')

def update_records(df, loc, filename):
    df.iloc[loc, df.columns.get_loc('used')] = '1'    
    df.to_csv(filename, columns=['idx','title','url','shorturl','date','used','priority'], encoding='utf-8')    

def select_data_record(df):
    n_rows = len(df.index) 
    selected_row = random.randint(0, n_rows-1)
    return df.iloc[selected_row,:]

# Get an ununused record
def select_data_record_not_used(df):
    selected_row = 0
    df_sub = df.loc[df['used'] == 0]
    df_priority = df_sub.loc[df_sub['priority'] == 1]
    if len(df_priority) > 0:
        print("High priority news found!")
        selected_row = df_priority.index
    else:
        print("No high priority news found or the record was already used")
        n_rows = len(df_sub.index) 
        selected_row = random.randint(0, n_rows-1)
    
    #print(selected_row)
    return df.iloc[selected_row,:]        

def read_all_records(filename):
    fname = filename
    df = []
    if path.exists(fname) == True:
        df = pd.read_csv(fname)
    return df
    
def read_records():
    return read_all_records(_filename)    

def is_database_new():
    db_new = False
    #print("Checking if the file is of today or not")  
    path = Path(_filename)
    timestamp = date.fromtimestamp(path.stat().st_mtime)
    if date.today() == timestamp:
        #Do Something
        #print("It was created today")
        db_new = True
    else:
        #print("It is old!")
        db_new = False
    return db_new

##### Main Method #####
def get_data_records():
    df = read_records()
    if (len(df) > 0): # Try to use existing RSS feeds, i.e., the current db
        print("DB Exists")
        if not is_database_new(): # See if the DB is new
            print("DB is old...creating a new one now...")
            df = download_websites(_number_of_records, True)
            store_records(df, _filename)
            dr = select_data_record(df)
        else:  
            print("DB is OK!...fetching random record now...")      
            # Check if there is a recent entry
            dr = select_data_record_not_used(df)
            #print(dr["idx"])           
    else:
        print("DB Does Not Exist...generating a new one now...") # Download RSS feeds, i.e., the db does not exist
        # download 
        df = download_websites(_number_of_records, True)
        store_records(df, _filename)
        dr = select_data_record(df)
 
    update_records(df, dr["idx"], _filename)
    return dr        
