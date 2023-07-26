from google.cloud import bigquery
from google.oauth2 import service_account

# TODO(developer): Set key_path to the path to the service account key
#                  file.
key_path = "/path/al/key.json"

credentials = service_account.Credentials.from_service_account_file(key_path)

client = bigquery.Client(credentials=credentials, project=credentials.project_id,)
# Query your BigQuery table
query = '''
SELECT *
FROM `tripulacionesgrupo5.app_dataset.app_test_table2`
LIMIT 10'''
query_job = client.query(query)

results = query_job.result()

# Print the results
for row in results:
    print(row)