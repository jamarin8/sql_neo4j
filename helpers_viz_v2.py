data = []

# Distinguishing attributes for nodes
node_keys = {'name_dob', 'account_id', 'business_name_legal',
             'business_name_dba', 'business_address', 'business_phone',
             'mobile_phone', 'ein', 'ssn', 'email_address', 'address', 'ip_address',
             'fraud_flag'}

for record in results_dict:
    path = record['path']
    nodes = []
    relationships = []
    if path:  # path is not empty
        central_node = path[0].get("account_id", "")
    for r in path:
        if isinstance(r, dict):
            if any(key in r for key in node_keys):
                node = {
                    key: r.get(key, 'NULL').strip() for key in node_keys
                }
                nodes.append(node)
                # Each node is also considered a relationship
                if central_node and node.get("account_id") != central_node:
                    relationships.append({"startNode": central_node, "endNode": node.get("account_id"), "properties": node})

    data.append({"nodes": nodes, "relationships": relationships})

def visualize_object(driver, data):
    graph = {
        "nodes": [],
        "relationships": []
    }

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
            graph["relationships"].append({
                "startNode": relationship.get("startNode"),
                "endNode": relationship.get("endNode"),
                "type": "LINKED_TO",
                "properties": relationship.get("properties")
            })

    return graph
