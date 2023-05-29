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

    added_nodes = set()

    for record in data:
        for node in record["nodes"]:
            account_id = node.get("account_id")
            if account_id not in added_nodes:
                added_nodes.add(account_id)
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
        for relationship in record["relationships"]:
            graph["relationships"].append({
                "startNode": relationship.get("startNode"),
                "endNode": relationship.get("endNode"),
                "type": relationship.get("type").upper()  # assuming the relationship type is in the 'type' key
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

