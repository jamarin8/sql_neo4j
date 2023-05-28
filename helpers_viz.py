
def visualize_object(driver, results):
    graph = {
        "nodes": [
            {
                "account_id": result["n"]["account_id"],
                "label": "Application",
                "name_dob": result["n"]["name_dob"],
                "business_name_legal": result["n"]["business_name_legal"],
                "business_name_dba": result["n"]["business_name_dba"],
                "business_address": result["n"]["business_address"],
                "business_phone": result["n"]["business_phone"],
                "mobile_phone": result["n"]["mobile_phone"],
                "ein": result["n"]["ein"],
                "ssn": result["n"]["ssn"],
                "email_address": result["n"]["email_address"],
                "address": result["n"]["address"],
                "ip_address": result["n"]["ip_address"]
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
            for relationship in result["n"][key]:
                graph["relationships"].append({
                    "startNode": result["n"]["account_id"],
                    "endNode": relationship["account_id"],
                    "type": key.upper()
                })

    return graph

