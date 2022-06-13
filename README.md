# simple_etl
Simple ETL managed by Airflow
This ETL is a sample data pipeline for extracting the data from https://jmcauley.ucsd.edu/data/amazon/links.html

Data consist of these fields:
{"asin", "title", "price","imUrl", "related", "salesRank", "brand", "categories"}

System is tested with these data sources: 
http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/meta_Amazon_Instant_Video.json.gz
http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/meta_Musical_Instruments.json.gz

Python's requests module is being used for sending HTTP requests. At the beginning of download response status is checked.If it is 200 then content is downloaded partially with a given chunk size.

Pandas module is used for organizing the data for transformation. Duplicate rows are removed and rows are cleaned.

Transformed data is loaded into the postgresql database with the engine and pd.to_sql methods.

A dimensional model is suggested in init-db.sql.

Airflow is used for scheduling with dags. Three different tasks are defined to run in three different times in a day. They are same tasks. One of them is original.
Others are imported from it. The only difference is their scheduled time.

Postgres and Airflow are containerized form scaling up scenarios.

To use the repo:
create an .env file containing:
POSTGRES_DB=DB_NAME
POSTGRES_USER=postgres
POSTGRES_PASSWORD=strong_password
POSTGRES_PORT=5432

To start the postgres container enther the commands below to bash screen:
source .env

docker-compose --env-file ./.env -f ./postgres-docker-compose.yaml up -d

To start Airflow container, first enter the commands to the bash screen:
chmod -R 777 ./dags ./logs ./plugins

echo -e "AIRFLOW_UID=$(id -u)" >> .env

echo -e "AIRFLOW_GID=0" >> .env

For starting the Airflow databases and creating the users we need to enter this command:
docker-compose -f airflow-docker-compose.yaml up airflow-init

Finally we will re-run the containers for running in background.
docker-compose -f airflow-docker-compose.yaml up -d

Go to http://localhost:8080 from web browser. Click on DAGs. You will see three predefined DAGs.
You can activate the DAGs to perfom their schedules.

Feel free to ask me any questions regarding the repo!

