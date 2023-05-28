def visualize_object(driver, results):
    graph = {
        "nodes": [
            {
                "account_id": result["account_id"],
                "label": "Application",
                "name_dob": result["name_dob"],
                "business_name_legal": result["business_name_legal"],
                "business_name_dba": result["business_name_dba"],
                "business_address": result["business_address"],
                "business_phone": result["business_phone"],
                "mobile_phone": result["mobile_phone"],
                "ein": result["ein"],
                "ssn": result["ssn"],
                "email_address": result["email_address"],
                "address": result["address"],
                "ip_address": result["ip_address"]
            }
            for result in results
        ],
        "relationships": []
    }

    keys = ['name_dob', 'account_id', 'business_name_legal',
            'business_name_dba', 'business_address', 'business_phone',
            'mobile_phone', 'ein', 'ssn', 'email_address', 'address', 'ip_address',
            'fraud_flag']

    for key in keys:
        for result in results:
            for relationship in result[key]:  # Assuming result[key] is a list of relationship dictionaries
                graph["relationships"].append({
                    "startNode": result["account_id"],
                    "endNode": relationship["account_id"],  # Assuming relationship is a dictionary with an "account_id" key
                    "type": key.upper()
                })

    return graph
