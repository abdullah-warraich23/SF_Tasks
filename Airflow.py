from datetime import datetime, timedelta
import subprocess
import os
import shutil
import pandas as pd
import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

# Configuration
REPO_URL = "https://github.com/abdullah-warraich23/SF_Tasks.git"
LOCAL_REPO_PATH = "C:/Users/userOneDrive/Desktop/SoftwareFinder_Tasks"

default_args = {
    'owner': 'automation_team',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 6),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
}

dag = DAG(
    'automated_web_tests',
    default_args=default_args,
    description='Automates web crawling, test execution, load test and Power BI update from Git',
    schedule_interval='@daily',  # Adjust schedule as needed
    catchup=False
)

def update_repo():
    """
    Clones the repository to a temporary folder if not present,
    otherwise pulls the latest changes.
    """
    if os.path.isdir(LOCAL_REPO_PATH):
        print("Repository already exists. Pulling latest changes...")
        result = subprocess.run(["git", "-C", LOCAL_REPO_PATH, "pull"],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to pull repo: {result.stderr}")
        print(result.stdout)
    else:
        print("Cloning repository...")
        result = subprocess.run(["git", "clone", REPO_URL, LOCAL_REPO_PATH],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to clone repo: {result.stderr}")
        print(result.stdout)

def run_crawler():
    """
    Pulls the latest code from Git and executes the web crawler script.
    """
    update_repo()
    crawler_script = os.path.join(LOCAL_REPO_PATH, "web_crawler.py")
    print(f"Running web crawler script: {crawler_script}")
    result = subprocess.run(["python", crawler_script],
                            capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"Web crawling failed: {result.stderr}")

web_crawler_task = PythonOperator(
    task_id='run_web_crawler',
    python_callable=run_crawler,
    dag=dag
)

def run_tests():
    """
    Pulls the latest code from Git and runs the automated tests.
    """
    update_repo()
    test_script = os.path.join(LOCAL_REPO_PATH, "automated_tests.py")
    print(f"Running test script: {test_script}")
    # Using pytest to run tests
    result = subprocess.run(["pytest", test_script],
                            capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"Test execution failed: {result.stderr}")

test_execution_task = PythonOperator(
    task_id='execute_tests',
    python_callable=run_tests,
    dag=dag
)

def run_load_test():
    """
    Runs the load test using pytest and saves results to CSV files.
    """
    update_repo()
    load_test_script = os.path.join(LOCAL_REPO_PATH, "LoadTest.py")
    print(f"Running load test script: {load_test_script}")
    
    # Run pytest with the load test script
    result = subprocess.run(["pytest", load_test_script], capture_output=True, text=True)
    print(result.stdout)
    
    if result.returncode != 0:
        raise Exception(f"Load test failed: {result.stderr}")
    
    # Move load test results to the data directory
    load_test_results_dir = os.path.join(LOCAL_REPO_PATH, "load_test_results")
    data_dir = os.path.join(LOCAL_REPO_PATH, "data")
    
    for file in os.listdir(load_test_results_dir):
        if file.endswith(".csv"):
            shutil.move(
                os.path.join(load_test_results_dir, file),
                os.path.join(data_dir, file)
            )
    print("Load test results moved to data directory.")

load_test_task = PythonOperator(
    task_id='run_load_test',
    python_callable=run_load_test,
    dag=dag
)


def update_csv():
    """
    Updates CSV files with the latest test and load test results.
    """
    update_repo()
    data_dir = os.path.join(LOCAL_REPO_PATH, "data")
    
    # Define paths to CSV files
    test_results_path = os.path.join(data_dir, "test_results.csv")
    load_test_results_path = os.path.join(data_dir, "loadtest_stats.csv")
    
    # Check if new load test results exist
    if not os.path.isfile(load_test_results_path):
        raise Exception(f"Load test results file not found: {load_test_results_path}")
    
    # Load existing test results (if any)
    if os.path.isfile(test_results_path):
        test_results = pd.read_csv(test_results_path)
    else:
        test_results = pd.DataFrame()
    
    # Load new load test results
    load_test_results = pd.read_csv(load_test_results_path)
    
    # Merge or append results
    updated_results = pd.concat([test_results, load_test_results], ignore_index=True)
    updated_results.to_csv(test_results_path, index=False)
    print(f"Updated CSV file: {test_results_path}")

def prepare_local_data():
    """Copy CSV/HTML files from Git repo to local data directory"""
    local_data_dir = "C:/PowerBI_Data/SoftwareFinder"
    
    # Clean existing data
    if os.path.exists(local_data_dir):
        shutil.rmtree(local_data_dir)
    os.makedirs(local_data_dir)
    
    # Copy files
    repo_data_dir = os.path.join(LOCAL_REPO_PATH, "data")
    for file in os.listdir(repo_data_dir):
        if file.endswith((".csv", ".html")):
            shutil.copy(
                os.path.join(repo_data_dir, file),
                os.path.join(local_data_dir, file)
            )
    print(f"Copied files to {local_data_dir}")

def refresh_power_bi():
    """
    Triggers a Power BI dataset refresh using the Power BI REST API.
    """
    power_bi_url = "https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_ACCESS_TOKEN"  # valid token
    }
    response = requests.post(power_bi_url, headers=headers)
    if response.status_code != 202:
        raise Exception(f"Failed to refresh Power BI: {response.text}")
    print("Power BI refresh triggered successfully.")

power_bi_refresh_task = PythonOperator(
    task_id='refresh_power_bi',
    python_callable=refresh_power_bi,
    dag=dag
)

# Define task dependencies
web_crawler_task >> test_execution_task >> csv_update_task >> power_bi_refresh_task
