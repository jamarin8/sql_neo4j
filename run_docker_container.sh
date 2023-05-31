docker run \
	--publish=7475:7474 --publish 7688:7687 \
	--volume=/Users/JohnMarin//neo4j_pii/data:/data \
	--volume=/Users/JohnMarin//neo4j_pii/logs:/logs \
	--volume=/Users/JohnMarin//neo4j_pii/plugins:/plugins \
	--volume=/Users/JohnMarin//neo4j_pii/import:/var/lib/neo4j/import \
	--env NEO4J_apoc_export_file_enabled=true \
	--env NEO4J_apoc_import_file_enabled=true \
	--env NEO4J_apoc_import_file_use__neo4j__config=true \
	--env NEO4JLABS_PLUGINS=\[“apoc”\] \
	--env=NEO4J_AUTH=neo4j/testpii524 \
	--env NEO4j_dbms_security_procedures_unrestricted=apoc.* \
	--env=NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
	neo4j:4.4.8-community
