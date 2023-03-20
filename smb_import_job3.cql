
USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row
MERGE (app:Application {account_id: row.AccountID})
ON CREATE
    SET app.account_id = row.AccountID,
        app.submission_date = row.SubmissionDate,
        app.fraud_flag = row.FraudFlag,
        app.name_dob = row.NAME_DOB,
        app.business_name_dba = row.BusinessNameDBA,
        app.business_name_legal = row.BusinessNameLegal,
        app.address = row.AddressLine1c,
        app.business_address = row.BusinessAddressLine1c,
        app.mobile_phone = row.MobilePhone,
        app.business_phone = row.BusPhoneNbr,
        app.ssn = row.SSN,
        app.ein = row.BusTaxID,
        app.email_address = row.Email,
        app.ip_address = row.IPAddress;

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.Email is not null
MERGE (email:Email{email_address: row.Email });

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.Email is not null
MATCH (a:Application{account_id: row.AccountID}), (b:Email{email_address:row.Email})
MERGE (a)-[:HAS_EMAIL]->(b);

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.MobilePhone is not null
MERGE (mp:MobilePhone{mobile_phone: row.MobilePhone });

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.MobilePhone is not null
MATCH (a:Application{account_id: row.AccountID}), (b:MobilePhone{mobile_phone: row.MobilePhone })
MERGE (a)-[:HAS_MOBILE_PHONE]->(b);

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.BusPhoneNbr is not null
MERGE (b:BusPhoneNbr{business_phone: row.BusPhoneNbr });

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.BusPhoneNbr is not null
MATCH (a:Application{account_id: row.AccountID}), (b:BusPhoneNbr{business_phone: row.BusPhoneNbr })
MERGE (a)-[:HAS_BUSINESS_PHONE]->(b);

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.SSN is not null
MERGE (b:SSN{social_security: row.SSN });

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.SSN is not null
MATCH (a:Application{account_id: row.AccountID}), (b:SSN{social_security: row.SSN })
MERGE (a)-[:HAS_SSN]->(b);

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.BusTaxID is not null
MERGE (b:EIN{ein: row.BusTaxID });

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.BusTaxID is not null
MATCH (a:Application{account_id: row.AccountID}), (b:EIN{ein: row.BusTaxID })
MERGE (a)-[:HAS_EIN]->(b);

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.IPAddress is not null
MERGE (b:IP_ADDRESS{ip_address: row.IPAddress});

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.IPAddress is not null
MATCH (a:Application{account_id: row.AccountID}), (b:IP_ADDRESS{ip_address: row.IPAddress})
MERGE (a)-[:HAS_IP_ADDRESS]->(b);

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.AddressLine1c is not null
MERGE (b:ADDRESS{address1: row.AddressLine1c});

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.AddressLine1c is not null
MATCH (a:Application{account_id: row.AccountID}), (b:ADDRESS{address1: row.AddressLine1c})
MERGE (a)-[:HAS_ADDRESS]->(b);

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.BusinessAddressLine1 is not null
MERGE (b:BUSINESS_ADDRESS{business_address1: row.BusinessAddressLine1});

USING PERIODIC COMMIT 50000 LOAD CSV WITH HEADERS FROM "<CSV_FILE_PATH>" AS row
WITH row WHERE row.BusinessAddressLine1 is not null
MATCH (a:Application{account_id: row.AccountID}), (b:BUSINESS_ADDRESS{business_address1: row.BusinessAddressLine1})
MERGE (a)-[:HAS_BUSINESS_ADDRESS]->(b);
