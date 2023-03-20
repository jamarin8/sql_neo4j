from apscheduler.schedulers.blocking import BlockingScheduler
import datetime as dt
import time
import pyodbc
import re
import pytz
import datetime as dt
from street_helper import street_abbreviations
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')
import os
import shutil
from logging_config import setup_logger

logger = setup_logger('output.log')

from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "mypassword"

print('running sql connect file...')

driver_sql = "ODBC Driver 17 for SQL Server"
server = "EC2AMAZ-VOB6UK7"
database = "test"

conn_str = (
    f'DRIVER={driver_sql};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'Trusted_Connection=yes;'
)


def read_sql_file(filepath):
    with open(filepath, 'r') as f:
        sql = f.read()
    return sql


job_map_select = {
    'job1': read_sql_file('query_1.sql'),
    'job2': read_sql_file('query_2.sql')
}


def sql_records_intake_clean(job, conn_str):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    records = cursor.execute(job_map_select[job]).fetchall()
    columnz = [c[0] for c in cursor.description]
    print(time.localtime())
    df_records = pd.DataFrame.from_records(data=records, columns=columnz)
    df_out = df_records.copy()
    df_out.rename(columns={'App1FirstName': 'FirstName',
                           'App1LastName': 'LastName',
                           'App1SSN': 'SSN',
                           'App1CurAddressLine1': 'AddressLine1',
                           'App1CurAddressLine2': 'AddressLine2',
                           'App1CurZipCode': 'ZipCode',
                           'App1Email': 'Email',
                           'App1MobilePhoneNbr': 'MobilePhone',
                           'App1DateOfBirth': 'DOB',
                           'App1CurAptSuiteNbr': 'SuiteNbr',
                           'App1CurCity': 'City',
                           'App1CurStateCode': 'State'}, inplace=True)

    def address_standardize(textexample):
        for k, v in street_abbreviations.items():
            if textexample.strip() == 'nan':
                return np.nan
            else:
                f = re.sub(r'\b{}\b'.format(k), v, textexample)
                if f != textexample:
                    textexample = f
        return textexample

    df_out['SubmissionDate'] = pd.to_datetime(df_out['SubmissionDate'])
    df_out['SubmissionDate'] = df_out['SubmissionDate'].dt.strftime('%Y-%m-%d')

    df_out['DOB'] = df_out['DOB'].astype(str)
    if 250125 in df_out['AccountID']:
        if df_out.loc[250125, 'DOB'] == '9661-05-01 00:00:00':
            df_out.loc[250125, 'DOB'] = '1966-01-15 00:00:00'
    df_out['DOB'] = pd.to_datetime(df_out['DOB'])
    df_out['DOB'] = df_out['DOB'].dt.strftime('%Y-%m-%d')
    df_out['NAME_DOB'] = df_out.agg('{0[FirstName]}_{0[LastName]}_{0[DOB]}'.format, axis=1).map(lambda x: x.upper())

    df_out.loc[(~df_out['BusPhoneNbr'].isnull()), 'BusPhoneNbr'] = \
        df_out.loc[(~df_out['BusPhoneNbr'].isnull()), 'BusPhoneNbr'].astype(str).str.replace(
            '^(\d{3})(\d{3})(\d{4})$',
            r'(\1) \2-\3', regex=True)

    df_out.loc[(~df_out['MobilePhone'].isnull()), 'MobilePhone'] = \
        df_out.loc[(~df_out['MobilePhone'].isnull()), 'MobilePhone'].astype(str).str.replace(
            '^(\d{3})(\d{3})(\d{4})$',
            r'(\1) \2-\3', regex=True)

    for col in ['BusinessZipCode']:
        df_out.loc[(df_out[col].isnull()), col] = pd.NA
        df_out.loc[(~df_out[col].isnull()), col] = \
            df_out.loc[(~df_out[col].isnull()), col].astype(str).str.strip().str.extract(r'(\d{,5})', expand=False)
    for col in ['ZipCode']:
        df_out.loc[(df_out[col].isnull()), col] = pd.NA
        df_out = df_out.assign(
            ZipCode=df_out.loc[(~df_out[col].isnull()), col].astype(str).str.strip().str.extract(r'(\d{,5})',
                                                                                                 expand=False))
    for col in ['FirstName', 'LastName', 'AddressLine1', 'AddressLine2', 'BusinessAddressLine1',
                'BusinessAddressLine2',
                'SuiteNbr', 'City']:
        df_out.loc[(df_out[col].isnull()), col] = np.nan
        df_out.loc[(~df_out[col].isnull()), col] = df_out.loc[(~df_out[col].isnull()), col].str.upper().replace(
            r'\.',
            r'',
            regex=True)
        df_out.loc[(~df_out[col].isnull()), col] = df_out.loc[(~df_out[col].isnull()), col].replace("\s{2,}", " ",
                                                                                                    regex=True).str.strip()

    df_out['AddressLine1c'] = df_out['AddressLine1'].apply(lambda x: address_standardize(str(x)))

    df_out['BusinessAddressLine1c'] = df_out['BusinessAddressLine1'].apply(lambda x: address_standardize(str(x)))

    for col in ['BusinessNameLegal', 'BusinessNameDBA']:
        df_out.loc[(df_out[col].isnull()), col] = np.nan
        df_out.loc[(~df_out[col].isnull()), col] = df_out.loc[(~df_out[col].isnull()), col].astype(str).str.upper()

    df_out.loc[(df_out['Email'].isnull()), 'Email'] = np.nan
    df_out.loc[(~df_out['Email'].isnull()), 'Email'] = df_out.loc[(~df_out['Email'].isnull()), 'Email'].str.lower()

    df_out.loc[(df_out['SSN'].isnull()), 'SSN'] = np.nan
    df_out.loc[(df_out['BusTaxID'].isnull()), 'BusTaxID'] = np.nan
    df_out.loc[(df_out['IPAddress'].isnull()), 'IPAddress'] = np.nan

    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    df_out.to_csv(f'sql_intake_{job}.csv', index=False)
    logger.info(f'sql_intake_{job}.csv formatted and created')

    return df_out[['AddressLine1', 'AddressLine1c', 'BusinessAddressLine1', 'BusinessAddressLine1c']]


def job1():
    job = 'job1'
    # running this creates the csv file that copies onto the neo4j import
    # therefore the out capture is for testing debugging only
    open('output.log', 'w').close()
    logger.info('LOG FILE INITIALIZED')
    job1_out = sql_records_intake_clean(job, conn_str)
    source_path = f"C:\\Users\\Administrator\\Documents\\SQL_Helpers_Neo4j\\neo4j_flask_app_dir\\sql_intake_{job}.csv"
    destination_path = f"C:\\tools\\neo4j-community\\neo4j-community-3.5.1\\import\\sql_intake_{job}.csv"
    shutil.copy(source_path, destination_path)
    logger.info(f'sql_intake_{job}.csv file copied to neo4j import folder')

    driver_neo = GraphDatabase.driver(uri, auth=(username, password))

    # we delete all nodes in the first pull simulating the reality
    def delete_all_nodes_and_relationships():
        with driver_neo.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    delete_all_nodes_and_relationships()

    # this file refers to the just created csv now in neo4j import
    # each job creates it own csv file in the loop
    csv_file_path = f"file:///sql_intake_{job}.csv"

    def run_query(query):
        with driver_neo.session() as session:
            statements = query.strip().split(";")
            for statement in statements:
                if statement.strip():
                    session.run(statement)

    with open(r"C:\Users\Administrator\Documents\SQL_Helpers_Neo4j\neo4j_flask_app_dir\smb_import_mar23.cql",
              "r") as file:
        cypher_query = file.read()
        # Replace the placeholder in the .cql file with the actual CSV file path
        cypher_query = cypher_query.replace("<CSV_FILE_PATH>", csv_file_path)
        run_query(cypher_query)

    # this is not the final query and only here for testing debugging
    # query = "MATCH path=(a:Application)-[*1..2]-(e:Application) WHERE a<>e RETURN path"
    # with driver_neo.session() as session:
    #     result = session.run(query)
    #     for record in result:
    #         r1 = record['path']
    #         print (r1)

    driver_neo.close()

    print(f'\n{job} executed at:', dt.datetime.now())


def job2():
    job = 'job2'
    # running this creates the csv file that copies onto the neo4j import
    # therefore the out capture is for testing debugging only
    job2_out = sql_records_intake_clean(job, conn_str)
    source_path = f"C:\\Users\\Administrator\\Documents\\SQL_Helpers_Neo4j\\neo4j_flask_app_dir\\sql_intake_{job}.csv"
    destination_path = f"C:\\tools\\neo4j-community\\neo4j-community-3.5.1\\import\\sql_intake_{job}.csv"
    shutil.copy(source_path, destination_path)
    logger.info(f'sql_intake_{job}.csv file copied to neo4j import folder')

    driver_neo = GraphDatabase.driver(uri, auth=(username, password))

    # this file refers to the just created csv now in neo4j import
    # each job creates it own csv file in the loop
    csv_file_path = f"file:///sql_intake_{job}.csv"

    def run_query(query):
        with driver_neo.session() as session:
            statements = query.strip().split(";")
            for statement in statements:
                if statement.strip():
                    session.run(statement)

    with open(r"C:\Users\Administrator\Documents\SQL_Helpers_Neo4j\neo4j_flask_app_dir\smb_import_mar23.cql",
              "r") as file:
        cypher_query = file.read()
        # Replace the placeholder in the .cql file with the actual CSV file path
        cypher_query = cypher_query.replace("<CSV_FILE_PATH>", csv_file_path)
        run_query(cypher_query)

    # this is not the final query and only here for testing debugging
    # query = "MATCH path=(a:Application)-[*1..2]-(e:Application) WHERE a<>e RETURN path"
    # with driver_neo.session() as session:
    #     result = session.run(query)
    #     for record in result:
    #         r1 = record['path']
    #         print (r1)

    driver_neo.close()

    print(f'\n{job} executed at:', dt.datetime.now())


# create scheduler instance
scheduler = BlockingScheduler()


def create_iso_date_now(delay_seconds=5):
    pst_zone = pytz.timezone('America/Los_Angeles')
    pst_dt = dt.datetime.now(pst_zone) + dt.timedelta(seconds=delay_seconds)
    utc_dt = pst_dt.astimezone(pytz.utc)
    return utc_dt


def create_iso_date(hour, minute, second):
    pst_time = dt.time(hour, minute, second)
    pst_zone = pytz.timezone('America/Los_Angeles')
    pst_dt = dt.datetime.combine(dt.datetime.today(), pst_time)
    utc_dt = pst_zone.localize(pst_dt).astimezone(pytz.utc)
    return utc_dt


# add jobs to scheduler
# {'id': 'job2', 'time': create_iso_date(2,0,0), 'func': job2}
jobs = [
    {'id': 'job1', 'time': create_iso_date_now(), 'func': job1},
    {'id': 'job2', 'time': create_iso_date_now(45), 'func': job2}
]

for job in jobs:
    scheduler.add_job(id=job['id'],
                      func=job['func'],
                      trigger='cron',
                      hour=job['time'].hour,
                      minute=job['time'].minute,
                      second=job['time'].second)

# start scheduler
scheduler.start()

