import json
import math

def remove_duplicates(dicts):
    serialized = [json.dumps(d, sort_keys=True) for d in dicts]
    unique_serialized = set(serialized)
    unique_dicts = [json.loads(d) for d in unique_serialized]
    return unique_dicts     

def data_refactor(results_dict):

    data = []

    for result in results_dict:
        path = result['path']
        nodes = []
        relationships = []

        for i in range(0, len(path)):
            if i % 2 == 0:  # nodes are at even indices
                nodes.append(path[i])
            else:  # relationships are at odd indices
                relationships.append(path[i])

        data.append({
            "nodes": nodes,
            "relationships": relationships
        })

    return data

def data_refactor_2(refactored_results_dict):

    data = refactored_results_dict

    def remove_duplicates(dicts):
        serialized = [json.dumps(d, sort_keys=True) for d in dicts]
        unique_serialized = set(serialized)
        unique_dicts = [json.loads(d) for d in unique_serialized]
        return unique_dicts

    full = {}
    nodes = [];  relationships = []
    for element in data:
        a = element['nodes']
        b = element['relationships']
        for aa in a:
            nodes.append({k:v for k,v in aa.items()})
        relationships.append({k:v for k,v in b[0].items()})


    full['nodes'] = remove_duplicates(nodes)
    full['relationships'] = relationships

    return full 


def visualize_object(data):
    graph = {
        "nodes": [],
        "relationships": []
    }

    keys = ['name_dob', 'account_id', 'business_name_legal',
            'business_name_dba', 'business_address', 'business_phone',
            'mobile_phone', 'ein', 'ssn', 'email_address', 'address', 'ip_address']

    for record in data:
        nodes = record["nodes"]
        relationships = record["relationships"]

        if len(nodes) < 2:
            print(f"Warning: Skipping a path with fewer than two nodes: {nodes}")
            continue

        for node in nodes:
            account_id = node.get("account_id")
            if account_id is None:
                print(f"Warning: Skipping a node without an account ID: {node}")
                continue

            graph["nodes"].append({
                "account_id": account_id,
                "label": "Application",
                "name_dob": node.get("name_dob"),
                "business_name_legal": node.get("business_name_legal"),
                "business_name_dba": node.get("business_name_dba"),
                "business_address": node.get("business_address"),
                "business_phone": node.get("business_phone"),
                "mobile_phone": node.get("mobile_phone"),
                "ein": node.get("ein"),
                "ssn": node.get("ssn"),
                "email_address": node.get("email_address"),
                "address": node.get("address"),
                "ip_address": node.get("ip_address")
            })

        for i, relationship in enumerate(relationships):

            if i+1 >= len(nodes):
                print(f"Warning: Skipping a relationship without a corresponding end node: {relationship}")
                continue

            for key in keys:
                if key in relationship:
                    graph["relationships"].append({
                        "startNode": nodes[i].get("account_id"),
                        "endNode": nodes[i+1].get("account_id"),
                        "type": key.upper()
                    })

    graph["relationships"] = remove_duplicates(graph["relationships"])

    return graph


def visualize_object_2(data):

    graph = {
        "nodes": [],
        "relationships": []
    }

    keys = ['name_dob', 'account_id', 'business_name_legal',
            'business_name_dba', 'business_address', 'business_phone',
            'mobile_phone', 'ein', 'ssn', 'email_address', 'address', 'ip_address']

    for record in data:
        nodes = record["nodes"]
        relationships = record["relationships"]

        # if len(nodes) < 2:
        #     print(f"Warning: Skipping a path with fewer than two nodes: {nodes}")
        #     continue

        for i, node in enumerate(nodes):
            account_id = node.get("account_id")
            if account_id is None:
                print(f"Warning: Skipping a node without an account ID: {node}")
                continue

            graph["nodes"].append({
                "account_id": account_id,
                "label": "Application",
                "name_dob": node.get("name_dob"),
                "business_name_legal": node.get("business_name_legal"),
                "business_name_dba": node.get("business_name_dba"),
                "business_address": node.get("business_address"),
                "business_phone": node.get("business_phone"),
                "mobile_phone": node.get("mobile_phone"),
                "ein": node.get("ein"),
                "ssn": node.get("ssn"),
                "email_address": node.get("email_address"),
                "address": node.get("address"),
                "ip_address": node.get("ip_address")
            })

            # If there's a next node and a relationship, create an edge
            if i < len(nodes) - 1 : # and i < len(relationships):
                for relationship in relationships:
                    for key in relationship:
                        if key in keys:
                            graph["relationships"].append({
                                "startNode": nodes[i].get("account_id"),
                                "endNode": nodes[i + 1].get("account_id"),
                                "type": key.upper()
                            })

    graph["relationships"] = remove_duplicates(graph["relationships"])

    return graph

def transform_data_to_graph(data):
    graph = {
        "nodes": [],
        "relationships": []
    }

    for record in data:
        nodes = record["nodes"]
        relationships = record["relationships"]

        # Flatten nodes
        for node in nodes:
            if node not in graph['nodes']:
                graph['nodes'].append(node)

        # Process each pair of nodes with their corresponding relationship
        for i in range(len(nodes) - 1):
            for relationship in relationships:
                for key in relationship.keys():
                    edge = {"startNode": nodes[i]["account_id"], "endNode": nodes[i + 1]["account_id"], "type": key.upper()}
                    graph["relationships"].append(edge)

    graph["relationships"] = remove_duplicates(graph["relationships"])

    return graph

def transform_data_to_graph_(data):
    graph = {
        "nodes": [],
        "relationships": []
    }

    center_x = 200
    center_y = 200
    radius = 100

    for i, record in enumerate(data):
        nodes = record["nodes"]
        relationships = record["relationships"]

        for j, node in enumerate(nodes):
            if node not in graph["nodes"]:
                node_with_coordinates = node.copy()

                # Calculate angle based on node's position in the list
                angle = 2 * math.pi * j / len(nodes)

                # Calculate x and y based on angle
                node_with_coordinates["x"] = center_x + radius * math.cos(angle)
                node_with_coordinates["y"] = center_y + radius * math.sin(angle)

                graph["nodes"].append(node_with_coordinates)

        for i in range(len(nodes) - 1):
            for relationship in relationships:
                for key, value in relationship.items():
                    graph["relationships"].append({
                        "startNode": nodes[i]["account_id"],
                        "endNode": nodes[i + 1]["account_id"],
                        "type": key,
                        "value": value
                    })

    return graph

def check_types(obj):

    out = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"Key: {key}, Type: {type(value)}")
            out.append(check_types(value))

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            print(f"List Index: {i}, Type: {type(item)}")
            out.append(check_types(item))
    else:
        out = f"Type: {type(obj)}"

    return out

