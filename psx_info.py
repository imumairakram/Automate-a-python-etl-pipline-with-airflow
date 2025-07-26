import requests
from bs4 import BeautifulSoup
import sqlalchemy as sal
import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import time
import json


def extract_data(**kwargs):
    url = 'https://www.psx.com.pk/market-summary/#main'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    container = soup.find('div', class_='col-sm-12 tab-pane inner-content-table automobile-div active')
    rows = container.find_all('tr', class_='red-text-td')
    
    dictionary = {
        'titles': [],
        'ldcp': [],
        'opens': [],
        'high': [],
        'low': [],
        'current': [],
        'change': [],
        'volume': [],
        'scrap_time': []
    }

    for row in rows:
        a = row.find_all('td')
        dictionary['titles'].append(a[0].text.strip())
        dictionary['ldcp'].append(a[1].text.strip())
        dictionary['opens'].append(a[2].text.strip())
        dictionary['high'].append(a[3].text.strip())
        dictionary['low'].append(a[4].text.strip())
        dictionary['current'].append(a[5].text.strip())
        dictionary['change'].append(a[6].text.strip())
        dictionary['volume'].append(a[7].text.strip())
        dictionary['scrap_time'].append(str(datetime.now()))

    kwargs['ti'].xcom_push(key='extracted_data', value=dictionary)
    print(f'✅ Data of {len(dictionary["titles"])} lines extracted successfully.')


def transform_data(**kwargs):
    ti = kwargs['ti']
    dictionary = ti.xcom_pull(key='extracted_data', task_ids='extract_data')

    df = pd.DataFrame(dictionary)
    df = df.replace(',', '', regex=True)
    df = df.replace('', pd.NA)

    type_conv = {
        'ldcp': float,
        'opens': float,
        'high': float,
        'low': float,
        'current': float,
        'change': float,
        'volume': float
    }

    for i in type_conv:
        df[i] = pd.to_numeric(df[i], errors='coerce')

    df['day_range'] = df['high'] - df['low']
    df['volatility_perc'] = ((df['high'] - df['low']) / df['opens']) * 100
    df_volatile = df.nlargest(5, 'volatility_perc')
    df_high = df.nlargest(5, 'change')
    df_low = df.nsmallest(5, 'change')

    ti.xcom_push(key='df', value=df.to_json())
    ti.xcom_push(key='df_volatile', value=df_volatile.to_json())
    ti.xcom_push(key='df_high', value=df_high.to_json())
    ti.xcom_push(key='df_low', value=df_low.to_json())


def create_connection():
    conn_str = 'mssql://Kabir-Khan-PC/airflowProject?driver=ODBC+DRIVER+17+FOR+SQL+SERVER'
    try:
        engine = sal.create_engine(conn_str)
        conn = engine.connect()
        print("✅ Connected to SQL Server successfully!")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to SQL Server: {e}")
        return None


def insert_data(**kwargs):
    ti = kwargs['ti']
    df = pd.read_json(ti.xcom_pull(key='df', task_ids='transform_data'))
    df_volatile = pd.read_json(ti.xcom_pull(key='df_volatile', task_ids='transform_data'))
    df_high = pd.read_json(ti.xcom_pull(key='df_high', task_ids='transform_data'))
    df_low = pd.read_json(ti.xcom_pull(key='df_low', task_ids='transform_data'))

    conn = create_connection()
    if not conn:
        return

    try:
        df.to_sql('psx_info', con=conn, index=False, if_exists='append')
        print(f"✅ Inserted {len(df)} rows into psx_info.")
    except Exception as e:
        print(f"❌ Error inserting psx_info: {e}")

    try:
        df_volatile.to_sql('psx_volatile', con=conn, index=False, if_exists='append')
        print(f"✅ Inserted {len(df_volatile)} rows into psx_volatile.")
    except Exception as e:
        print(f"❌ Error inserting psx_volatile: {e}")

    try:
        df_high.to_sql('psx_high_performance', con=conn, index=False, if_exists='append')
        print(f"✅ Inserted {len(df_high)} rows into psx_high_performance.")
    except Exception as e:
        print(f"❌ Error inserting psx_high_performance: {e}")

    try:
        df_low.to_sql('psx_low_performance', con=conn, index=False, if_exists='append')
        print(f"✅ Inserted {len(df_low)} rows into psx_low_performance.")
    except Exception as e:
        print(f"❌ Error inserting psx_low_performance: {e}")


# Define the DAG
default_args = {
    'owner': "Kabir",
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='psx_stock_etl',
    default_args=default_args,
    description='ETL pipeline for PSX data',
    schedule='0 22 * * *',
    start_date=datetime(2025, 5, 3),
    catchup=False,
    tags=['stock_daily'],
) as dag:

    extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        provide_context=True,
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True,
    )

    insert = PythonOperator(
        task_id='insert_data',
        python_callable=insert_data,
        provide_context=True,
    )

    extract >> transform >> insert
