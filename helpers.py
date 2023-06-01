
Invoke-WebRequest -Uri "https://download.mozilla.org/?product=firefox-latest&os=win&lang=en-US" -OutFile "firefox_installer.exe"

from itertools import permutations

results_dict = []
for record in results:
    path = []
    for node in record['path'].nodes:
        path.append(node._properties)
    for relationship in record['path'].relationships:
        path.append(relationship._properties)
    results_dict.append({'path': path})

#

friends = set()
first = set()
rest = set()

for record in results_dict:
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

def fix_year(year: object, min_year: object = 1900, max_year: object = 2023) -> object:
    """Attempt to fix an out-of-range year by permuting its digits."""
    perms = [''.join(p) for p in permutations(year)]
    for yr in perms:
        if min_year <= int(yr) <= max_year:
            return yr
    return None  # no valid permutations found

def clean_dates(df, column, min_year=1900, max_year=2023):
    for i in df.index:
        year = df.loc[i, column][:4]
        if not (min_year <= int(year) <= max_year):
            # Try to fix the year
            new_year = fix_year(year)
            if new_year is not None:
                # If a valid permutation was found, replace the year
                df.loc[i, column] = new_year + df.loc[i, column][4:]
            else:
                # If no valid permutations, replace with a default date
                df.loc[i, column] = '1900-01-01 00:00:00'
    return df


import os

def get_neo4j_import_directory_windows():
    # Define the rest of the path
    rest_of_path = ".Neo4jDesktop\\distributions\\neo4j\\neo4j-enterprise-5.3.0-windows\\neo4j-enterprise-5.3.0\\import"

    try:
        # Obtain the HOME directory
        home_directory = os.getenv("USERPROFILE")
        # Join the paths
        main_path = os.path.join(home_directory, rest_of_path)
        if os.path.exists(main_path):
            return main_path
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        print("Main path not found. Searching for backup path...")

        # Define the backup path pattern
        backup_path_pattern = os.path.join(home_directory, ".Neo4jDesktop", "distributions", "neo4j",
                                           "neo4j-enterprise-*", "import")
        backup_paths = glob.glob(backup_path_pattern)

        if backup_paths:
            print("Backup path found.")
            return backup_paths[0]
        else:
            raise FileNotFoundError("Neither the main path nor a backup path could be found.")
