from flask import Flask, render_template, request, jsonify
from neo4j import GraphDatabase
import json
import re
import numpy as np
import pandas as pd

import datetime as dt
import time
import pyodbc
import pytz
from street_helper import street_abbreviations
import os
import shutil
from logging_config import setup_logger

logger = setup_logger('output.log')

driver_sql = "ODBC Driver 17 for SQL Server"
server = "EC2AMAZ-XXXX"
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
    'job3': read_sql_file('query_3.sql')
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

    return


def job3():
    job = 'job3'
    # running this creates the csv file that copies onto the neo4j import
    # therefore the out capture is for testing debugging only
    job2_out = sql_records_intake_clean(job, conn_str)
    source_path = f"C:\\Users\\Administrator\\Documents\\SQL_Helpers_Neo4j\\neo4j_flask_app_dir\\sql_intake_{job}.csv"
    destination_path = f"C:\\tools\\neo4j-community\\neo4j-community-3.5.1\\import\\sql_intake_{job}.csv"
    shutil.copy(source_path, destination_path)
    logger.info(f'sql_intake_{job}.csv file copied to neo4j import folder')
    username = "neo4j"
    password = "mypassword"
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

    with open(r"C:\Users\Administrator\Documents\SQL_Helpers_Neo4j\neo4j_flask_app_dir\smb_import_job3.cql",
              "r") as file:
        cypher_query = file.read()
        # Replace the placeholder in the .cql file with the actual CSV file path
        cypher_query = cypher_query.replace("<CSV_FILE_PATH>", csv_file_path)
        run_query(cypher_query)

    driver_neo.close()

    print(f'\n{job} executed at:', dt.datetime.now())


search = """
MATCH path=(a:Application)-[*1..4]-(e:Application) WHERE a<>e AND a.account_id = $account_id RETURN path LIMIT 300
"""

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "mypassword"))


def fraud_query(tx, search, account_id):
    friends = set()

    results = tx.run(search, account_id=account_id)

    for record in results.data():
        print('******** PATH', record['path'])
        for r in record['path']:
            if isinstance(r, dict) and 'account_id' in r.keys():
                friends.add(
                    (r['name_dob'].strip(), r['account_id'].strip(), r.get('business_name_legal', 'NULL').strip(),
                     r.get('business_name_dba', 'NULL').strip(), r.get('business_address', 'NULL').strip(),
                     r.get('business_phone', 'NULL').strip(), r.get('mobile_phone', 'NULL').strip(),
                     r.get('ein', 'NULL').strip(), r.get('ssn', 'NULL').strip(),
                     r.get('email_address', 'NULL').strip(), r.get('address', 'NULL').strip(),
                     r.get('ip_address', 'NULL').strip(), r.get('fraud_flag', 'NULL').strip()
                     ))

    first = [x for x in list(friends) if x[1] == account_id]
    rest = [x for x in list(friends) if x[1] != account_id]
    rest.sort(key=lambda x: int(x[1]))
    combined = first + rest

    print('parse_results', combined)

    def capture_duplicates_in_df(intake):
        df = pd.DataFrame(intake, columns=['name_dob', 'account_id', 'business_name_legal',
                                           'business_name_dba', 'business_address', 'business_phone',
                                           'mobile_phone', 'ein', 'ssn', 'email_address', 'address', 'ip_address',
                                           'fraud_flag'])
        dups = []
        for col in [c for c in df.columns if 'fraud' not in c]:
            try:
                dup = list(set(df[col].loc[df.duplicated(col)]))
                dups.extend(dup)
            except:
                continue
        return dups

    duplicate_entries = capture_duplicates_in_df(friends)
    return combined, duplicate_entries


def getresults(account_id):
    with driver.session() as session:
        results, duplicate_entries = session.read_transaction(fraud_query, search, account_id)
        return results, duplicate_entries


def log_update():
    with open('output.log', 'r') as file:
        lines = file.readlines()

    job1_regex = re.compile(r'.*INFO.*job1.*created')
    job1_line = [line for line in lines if job1_regex.match(line)]
    job2_regex = re.compile(r'.*INFO.*job2.*created')
    job2_line = [line for line in lines if job2_regex.match(line)]
    job3_regex = re.compile(r'.*INFO.*job3.*created')
    job3_line = [line for line in lines if job3_regex.match(line)]

    if job2_line:
        job1_line.extend([job2_line[-1]])
    if job3_line:
        job1_line.extend([job3_line[-1]])

    info_lines = job1_line

    timestamp_regex = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}')

    sql_load_chron = []
    for line in info_lines:
        timestamp_match = timestamp_regex.search(line)
        if timestamp_match:
            timestamp_str = timestamp_match.group(0)[:-4]  # Remove the last 4 characters (",273")
            sql_load_chron.append(timestamp_str)

    return sql_load_chron


app = Flask(__name__)


@app.route('/')
def home():
    account_id = request.args.get('account_id')
    start_time = time.perf_counter()
    job3()
    results, duplicate_entries = getresults(account_id)
    end_time = time.perf_counter()
    elapsed_time = round(end_time - start_time, 4)
    num_connecting = len(results)
    sql_load_chron = log_update()
    return render_template('home.html', susp_app=results,
                           duplicates=duplicate_entries, acct_id=account_id,
                           num_connecting=num_connecting,
                           sql_load_chron=sql_load_chron,
                           elapsed_time=elapsed_time)


if __name__ == '__main__':
    app.run(debug=True)




