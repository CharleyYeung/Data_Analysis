from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
try:
    from airflow.providers.postgres.operators.postgres import PostgresOperator
except ImportError:
    from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator as PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.http.hooks.http import HttpHook
from datetime import datetime, timedelta
import logging
import json
import os
from airflow.models import Variable
import boto3

def fetch_and_save_tfl_status():
    # FETCH TFL API Data
    http = HttpHook(method='GET', http_conn_id='tfl_api_connection')
    response = http.run(endpoint='/Line/Mode/tube/Status')
    data = response.json()
    logging.info("Full API Response: \n" + json.dumps(data, indent=4))

    # PREPARE Postgres Hook (DIRECT TO DATABASE IN DOCKER)
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    for line in data:
        line_name = line.get('name')
        status_info = line.get('lineStatuses', [{}])[0]
        status_desc = status_info.get('statusSeverityDescription')
        status_reason = status_info.get('reason')
        sql = """
            INSERT INTO tfl_line_status (line_name, status_description, status_reason) 
            VALUES (%s, %s, %s)
        """
        pg_hook.run(sql, parameters=(line_name, status_desc, status_reason))
        
        # LOGGING
        if status_desc != "Good Service":
            reason_str = status_reason if status_reason else "No specific reason provided"
            logging.warning(f"⚠️ {line_name} is having: {status_desc}. Reason: {reason_str}")
        else:
            logging.info(f"✅ {line_name}: Good Service")

def clean_data_fn():
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    sql = """
        CREATE TABLE IF NOT EXISTS cleaned_tfl_status (
            id SERIAL PRIMARY KEY,
            line_name VARCHAR(50),
            is_disrupted BOOLEAN,
            cleaned_reason TEXT,
            checked_at TIMESTAMP
        );

        INSERT INTO cleaned_tfl_status (line_name, is_disrupted, cleaned_reason, checked_at)
        SELECT 
            line_name,
            CASE WHEN status_description != 'Good Service' THEN TRUE ELSE FALSE END,
            COALESCE(status_reason, 'Normal Operation'),
            timestamp
        FROM tfl_line_status
        WHERE timestamp > NOW() - INTERVAL '5 minutes';
    """
    pg_hook.run(sql)

def create_analytics_view_fn():
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    sql = """
        CREATE OR REPLACE VIEW tfl_gold_analytics AS
        WITH status_lag AS (
            SELECT 
                line_name,
                is_disrupted,
                cleaned_reason,
                checked_at,
                LEAD(checked_at) OVER (PARTITION BY line_name ORDER BY checked_at) as next_check_at
            FROM cleaned_tfl_status
        ),
        event_duration AS (
            SELECT 
                line_name,
                is_disrupted,
                checked_at,
                EXTRACT(HOUR FROM checked_at) as hour_of_day,
                EXTRACT(EPOCH FROM (next_check_at - checked_at))/60 as duration_minutes
            FROM status_lag
        )
        SELECT 
            line_name,
            SUM(CASE WHEN is_disrupted THEN 1 ELSE 0 END) as total_disruption_records,
            
               ROUND(AVG(CASE WHEN is_disrupted THEN duration_minutes END)::NUMERIC, 1) as avg_recovery_time_minutes,
            
            (
                SELECT hour_of_day 
                FROM event_duration ed 
                WHERE ed.line_name = event_duration.line_name AND ed.is_disrupted = TRUE
                GROUP BY hour_of_day 
                ORDER BY COUNT(*) DESC 
                LIMIT 1
            ) as peak_disruption_hour
        FROM event_duration
        GROUP BY line_name
        ORDER BY total_disruption_records DESC;
    """
    pg_hook.run(sql)

def export_live_json():
    # CONNECT TO POSTGRESQL AND FETCH LATEST STATUS
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # MOST RECENT STATUS PER LINE 
    sql = """
        SELECT DISTINCT ON (line_name) 
            line_name, is_disrupted, cleaned_reason
        FROM cleaned_tfl_status
        ORDER BY line_name, checked_at DESC;
    """
    
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    
    # JOIN DATA INTO A DICTIONARY STRUCTURE FOR JSON OUTPUT
    status_dict = {}
    for row in rows:
        line_name = row[0]
        status_dict[line_name] = {
            "is_disrupted": row[1],
            "reason": row[2]
        }
        
    # WRITE TO LOCAL FILE (FOR NOW) - IN PRODUCTION, THIS WOULD BE UPLOADED TO S3 OR ANOTHER CLOUD STORAGE
    output_path = '/tmp/status.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(status_dict, f, ensure_ascii=False, indent=4)
        
    logging.info(f"Successfully exported latest status to {output_path}!")
    logging.info("JSON content preview: " + json.dumps(status_dict, indent=2))

    # UPLOAD TO AWS S3
    try:
        # GET THE AWS CREDENTIALS FROM AIRFLOW VARIABLES (SECURELY STORED IN AIRFLOW UI) 
        aws_access_key = Variable.get("AWS_ACCESS_KEY_ID")
        aws_secret_key = Variable.get("AWS_SECRET_ACCESS_KEY")
        bucket_name = "tfl-live-map-charley"  # REPLACE WITH THE S3 BUCKET NAME
        
        # INITIALIZE S3 CLIENT
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name="eu-west-2" 
        )
        
        # UPLOAD Object Key NAMED status.json
        s3_client.upload_file(
            Filename=output_path, 
            Bucket=bucket_name, 
            Key='status.json',
            ExtraArgs={'ContentType': 'application/json'} 
        )
        logging.info(f"SUCCESSFULLY UPLOADED status.json TO S3 Bucket: {bucket_name}!")
        
    except Exception as e:
        logging.error(f"FAILED TO UPLOAD status.json TO S3 Bucket: {str(e)}")
        raise e


# DEFINE DAG
with DAG(
    dag_id='tfl_line_disruption_monitor',
    start_date=datetime(2026, 5, 1),
    schedule="*/30 0-1,5-23 * * *",  # EVERY 20 MINUTES DURING SERVICE HOURS(0-1AM AND 5-11PM)
    catchup=False
) as dag:

    # INITIALIZE TABLE
    create_table = PostgresOperator(
        task_id='create_table',
        conn_id='postgres_default',
        sql="""
            CREATE TABLE IF NOT EXISTS tfl_line_status (
                id SERIAL PRIMARY KEY,
                line_name VARCHAR(50),
                status_description TEXT,
                status_reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
    )

    # FETCH TFL STATUS AND SAVE TO POSTGRESQL
    get_status = PythonOperator(
        task_id='fetch_tube_status',
        python_callable=fetch_and_save_tfl_status
    )

    clean_data = PythonOperator(
        task_id='clean_data',
        python_callable=clean_data_fn
    )

    create_analytics_view = PythonOperator(
        task_id='create_analytics_view',
        python_callable=create_analytics_view_fn
    )

    export_json_task = PythonOperator(
        task_id='export_live_json',
        python_callable=export_live_json
    )

    # SET UP DEPENDENCIES
    create_table >> get_status >> clean_data >> [create_analytics_view, export_json_task]