import subprocess
import shlex
import pytest

# To register the custom marker
def pytest_configure(config):
    config.addinivalue_line("markers", "loadtest: mark test as a load test")

@pytest.mark.loadtest
def test_locust_load():
    # Defining the command with the target host:
    command = (
        "locust -f locust.py --headless -u 50 -r 5 --run-time 1m --host=https://www.softwarefinder.com"
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


    # 'pytest LoadTest.py -v' to run