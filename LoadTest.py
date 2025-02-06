import subprocess
import shlex
import pytest
import os

def merge_csv_files(csv_files, merged_file):
    """Merge multiple CSV files into a single CSV file."""
    with open(merged_file, "w", encoding="utf-8") as outfile:
        for csv in csv_files:
            if os.path.exists(csv):
                with open(csv, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read())
                    outfile.write("\n")
    return os.path.exists(merged_file)

@pytest.mark.loadtest
def test_locust_load():
    # The command remains the same except that we add CSV flags so that Locust saves its results.
    # By adding "--csv=locust_results", Locust will create:
    #    locust_results_stats.csv
    #    locust_results_failures.csv
    #    locust_results_stats_history.csv
    command = (
        "locust -f locust.py --headless -u 50 -r 5 --run-time 1m "
        "--host=https://www.softwarefinder.com --csv=locust_results"
    )
    print("Running Locust command:", command)
    
    result = subprocess.run(shlex.split(command), capture_output=True, text=True)
    
    with open("locust_output.log", "w", encoding="utf-8") as f:
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\nSTDERR:\n")
        f.write(result.stderr)
    if result.returncode != 0:
        print("Locust failed with error output:")
        print(result.stderr)
    
    assert result.returncode == 0, f"Locust failed with error:\n{result.stderr}"
    
    # List of CSV files produced by Locust
    csv_files = [
        "locust_results_stats.csv",
        "locust_results_failures.csv",
        "locust_results_stats_history.csv",
    ]
    
    # Merge them into a single CSV file
    merged_csv = "merged_locust_results.csv"
    merge_success = merge_csv_files(csv_files, merged_csv)
    assert merge_success, "Failed to merge CSV files"
    
    print("Merged CSV results saved to:", merged_csv)
