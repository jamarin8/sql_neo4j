def data_refactor(results_dict):
    data = []

    for result in results:
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

    return graph

