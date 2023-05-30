data = [{
    "nodes": [node._properties for node in record["path"].nodes],
    "relationships": [relationship._properties for relationship in record["path"].relationships]
} for record in result]

def visualize_object(driver, data):
    graph = {
        "nodes": [],
        "relationships": []
    }

    keys = ['name_dob', 'account_id', 'business_name_legal',
            'business_name_dba', 'business_address', 'business_phone',
            'mobile_phone', 'ein', 'ssn', 'email_address', 'address', 'ip_address',
            'fraud_flag']

    for record in data:
        for node in record["nodes"]:
            graph["nodes"].append({
                "account_id": node.get("account_id"),
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
        for relationship in record["relationships"]:
            for key in keys:
                if key in relationship:
                    graph["relationships"].append({
                        "startNode": relationship.get("startNode"),
                        "endNode": relationship.get("endNode"),
                        "type": key.upper()
                    })

    return graph


def visualize_object_2(driver, data):
    graph = {
        "nodes": [],
        "relationships": []
    }

    keys = ['name_dob', 'account_id', 'business_name_legal',
            'business_name_dba', 'business_address', 'business_phone',
            'mobile_phone', 'ein', 'ssn', 'email_address', 'address', 'ip_address',
            'fraud_flag']

    for record in data:
        nodes = record["nodes"]
        relationships = record["relationships"]

        if len(nodes) < 2:
            print(f"Warning: Skipping a path with fewer than two nodes: {nodes}")
            continue

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
            if i < len(nodes) - 1 and i < len(relationships):
                for relationship in relationships:
                    for key in relationship:
                        if key in keys:
                            graph["relationships"].append({
                                "startNode": nodes[i].get("account_id"),
                                "endNode": nodes[i + 1].get("account_id"),
                                "type": key.upper()
                            })

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
                    edge = {"startNode": nodes[i]["id"], "endNode": nodes[i + 1]["id"], key: relationship[key]}
                    graph["relationships"].append(edge)

    return graph


import math


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
                        "startNode": nodes[i]["id"],
                        "endNode": nodes[i + 1]["id"],
                        "type": key,
                        "value": value
                    })

    return graph



def check_types(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"Key: {key}, Type: {type(value)}")
            check_types(value)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            print(f"List Index: {i}, Type: {type(item)}")
            check_types(item)
    else:
        print(f"Type: {type(obj)}")

# Call the function on your graph dictionary
check_types(graph)

