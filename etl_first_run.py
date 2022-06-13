import os
import pandas as pd
from dotenv import dotenv_values
from sqlalchemy import create_engine,inspect
import sqlalchemy
import gzip
import time
import requests
from pathlib import Path
import logging
from functools import wraps
from datetime import datetime, timezone
from variables import *



table_name = 'raw_products'
urls = URLS

CONFIG = dotenv_values('.env')
if not CONFIG:
    CONFIG = os.environ

today = datetime.now()
log_time = today.strftime("%a_%b_%d_%Y_%X")
log_file = f'etl_{log_time}.log'
logging.basicConfig(filename=log_file,filemode='w', format='[%(levelname)s]: %(message)s', level=logging.DEBUG)

def logger(fn):

    @wraps(fn)
    def inner(*args, **kwargs):
        called_at = datetime.now(timezone.utc)
        print(f">>> Running {fn.__name__!r} function. Logged at {called_at}")
        logging.info(f">>> Running {fn.__name__!r} function. Logged at {called_at}")
        to_execute = fn(*args, **kwargs)
        print(f">>> Function: {fn.__name__!r} executed. Logged at {called_at}")
        logging.info(f">>> Function: {fn.__name__!r} executed. Logged at {called_at}")
        return to_execute

    return inner


def clean_cats(samp):
  new_smp = []
  for s in samp:
    new_smp.append(str(s))
  return new_smp

@logger
def connect_db():
    p_user = CONFIG["POSTGRES_USER"]
    p_pass = CONFIG["POSTGRES_PASSWORD"]
    p_port = CONFIG["POSTGRES_PORT"]
    p_db = CONFIG["POSTGRES_DB"]

    connection_uri = "postgresql://{}:{}@localhost:{}/{}".format(
        p_user,
        p_pass,
        p_port,
        p_db
    )
    engine = create_engine(connection_uri,pool_pre_ping=True)
    
    #test connection
    conn = engine.raw_connection()
    cur = conn.cursor()
    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    logging.info(db_version)
    print(db_version)

    return engine

#partial download checking request failures 
@logger
def download(url):
    filename = url.split('/')[-1]
    r = requests.get(url,stream=True)
    response_size = r.headers.get('content-length')
    if r.status_code == 200:
        logging.info(f'start downloading the file {filename}')
        logging.info(f"response_size: {response_size}")
        with open (filename,'ab') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
            file_size = Path(filename).stat().st_size
        return filename
    else:
        logging.error(f"bad response for {url}")
        return None
        
@logger
def extract(urls):
    for url in urls:
        path = download(url)
        if path:
            g = gzip.open(path, 'rb')
            for l in g:
                yield eval(l)

@logger
def transform(path):
    i = 0
    df = {}
    df_asin = {}

    count = 0
    engine = connect_db()
    
    for d in extract(path):
        df[i] = d
        i += 1

        
    logging.info(f"number of lines in source {i}")
    
    new_df = pd.DataFrame.from_dict(df,orient='index')
    
    #more efficient way of removing duplicate asins instead manual ways in the loop
    new_df.drop_duplicates(subset=['asin'])

    #preventing errors of case sensitivities
    new_df.columns = new_df.columns.str.strip().str.lower()

    #needed to manage nested lists with different dimensions which occurs when using different sources
    if 'categories' in new_df.columns:
        new_df['categories'] = new_df['categories'].map(lambda x: clean_cats(x))
    else:
        new_df['categories'] = [[]]

    return new_df

@logger
def load_data_to_db(df,table_name,engine):
    try:
        #send data to db, excluding index. Also fixing issues with dtype arguments.
        df.to_sql(
            name=table_name,
            con=engine,
            index=False,
            if_exists='append',
            dtype={
                "related": sqlalchemy.types.JSON,
                "salesrank": sqlalchemy.types.JSON
                }
            ) 

    except Exception as e:
        logging.info("error during loading")
        logging.info(e)

#checking total run time for tuning
start = time.time()
logging.info('timer started')
print('timer started')
df = transform(urls)

engine = connect_db()
engine.connect()
load_data_to_db(df,table_name,engine)

end = time.time()
total_time = end-start
logging.info(f'it took {total_time} seconds to transfer the data')
print(f'it took {total_time} seconds to transfer the data')


