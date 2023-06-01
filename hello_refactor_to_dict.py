from flask import Flask, render_template, request, jsonify
from neo4j import GraphDatabase
import json
import numpy as np
import pandas as pd

from helpers_viz import visualize_object, visualize_object_2
from helpers_viz import data_refactor, data_refactor_2
from helpers_viz import check_types 
from helpers_viz import transform_data_to_graph, transform_data_to_graph_


search = """
MATCH path=(a:Application)-[*1..4]-(e:Application) WHERE a<>e AND a.account_id = $account_id RETURN path LIMIT 300
"""

uri = "neo4j://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "mypassword"))


def fraud_query(tx, search, account_id):

    results = tx.run(search, account_id=account_id)

    results_dict = []

    for record in results:
        path = []
        for node in record['path'].nodes:
            path.append(node._properties)
        for relationship in record['path'].relationships:
            path.append(relationship._properties)
        results_dict.append({'path': path})

    return results_dict

def refine_results(results_dict, account_id):

    friends = set()
    first = set()
    rest = set()

    for record in results_dict:
        record['path'] = [path_dict for path_dict in record['path'] if path_dict]
        path = record['path']
        for r in path:
            if isinstance(r, dict) and 'account_id' in r.keys():
                friend_tuple = (
                    r.get('name_dob', '').strip(), r.get('account_id', '').strip(), r.get('business_name_legal', 'NULL').strip(),
                    r.get('business_name_dba', 'NULL').strip(), r.get('business_address', 'NULL').strip(),
                    r.get('business_phone', 'NULL').strip(), r.get('mobile_phone', 'NULL').strip(),
                    r.get('ein', 'NULL').strip(), r.get('ssn', 'NULL').strip(),
                    r.get('email_address', 'NULL').strip(), r.get('address', 'NULL').strip(),
                    r.get('ip_address', 'NULL').strip(), r.get('fraud_flag', 'NULL').strip()
                )
                friends.add(friend_tuple)
                if friend_tuple[1] == account_id:
                    first.add(friend_tuple)
                else:
                    rest.add(friend_tuple)

    first_list = list(first)
    rest_list = list(rest)
    rest_list.sort(key=lambda x: int(x[1]))
    combined_results = first_list + rest_list

    def capture_duplicates_in_df(intake_set):
        df = pd.DataFrame(intake_set, columns=['name_dob','account_id','business_name_legal',
        'business_name_dba','business_address','business_phone',
         'mobile_phone', 'ein', 'ssn', 'email_address','address', 'ip_address', 'fraud_flag'])
        dups = []
        for col in [c for c in df.columns if 'fraud' not in c]:
            try:
                dup = list(set(df[col].loc[df.duplicated(col)]))
                dups.extend(dup)
            except:
                continue
        return dups

    duplicate_entries = capture_duplicates_in_df(friends)
    return combined_results, duplicate_entries

def getresults(account_id):
    with driver.session() as session:
        results_dict = session.execute_read(fraud_query, search, account_id)
        return results_dict

app = Flask(__name__)

@app.route('/')
def home():
    account_id = request.args.get('account_id')
    results = getresults(account_id)
    combined_results, duplicate_entries = refine_results(results, account_id)

    # results = 'results is empty' if len(results) == 0 else results 

    data_ = data_refactor(results)
    data_print_1 = json.dumps(data_, indent=4)

    data = data_refactor_2(data_)
    data_print_2 = json.dumps(data, indent=4)

    graph = visualize_object(data_)
    graph_print = json.dumps(graph, indent=4)

    graph2 = visualize_object_2(data_)
    graph2_print = json.dumps(graph2, indent=4)

    graph3 = transform_data_to_graph_(data_)
    graph3_print = json.dumps(graph3, indent=4)

    num_connecting = len(combined_results)

    return render_template('home_old.html', susp_app=combined_results,
        duplicates=duplicate_entries, acct_id=account_id, 
        num_connecting=num_connecting, results=results, 
        graph3=graph3)


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5003)
