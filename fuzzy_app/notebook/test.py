import os
import pandas as pd
import logging
logger = logging.getLogger(__file__)
import warnings
from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.schema import *
warnings.filterwarnings("ignore")

# def read_data(connection_string:str, query:str):
#     engine = create_engine(connection_string)
#     with engine.connect() as conn:
#         df = pd.read_sql_query(query,con=conn)
    
#     return df


tb_name = "PERSONA_FUZZY_OUTPUT_1"
conn_string = os.environ['hive_secret']
query_str =f"select * from curation_corp_dev.{tb_name}"
logger.info("Reading data from hive...")
print("Reading data from hive...")
engine = create_engine(conn_string)
with engine.connect() as conn:
    df = pd.read_sql_query(query_str,con=conn)
logger.info(f"Loaded Data: {df.shape}")
print(f"Loaded Data: {df.shape}")
logger.info('Completed.')

