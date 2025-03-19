import pytest
import requests
import json
import os

# Define API endpoint
API_URL = "http://localhost:8000/run"  # Change if different

# Paths to test files
TEST_INPUT_PATH = "tests/test_input.json"
EXPECTED_OUTPUT_PATH = "tests/expected_output.json"

@pytest.fixture
def load_test_data():
    """Load test input and expected output."""
    with open(TEST_INPUT_PATH, "r") as f:
        test_input = json.load(f)
    
    with open(EXPECTED_OUTPUT_PATH, "r") as f:
        expected_output = json.load(f)

    return test_input, expected_output

def test_emp_api(load_test_data):
    """Send test input to the API and compare the response to the expected output."""
    test_input, expected_output = load_test_data

    # Send request to the API
    response = requests.post(API_URL, json=test_input)

    # Ensure request was successful
    assert response.status_code == 200, f"API call failed: {response.text}"

    # Convert response JSON to dictionary
    api_output = response.json()

    # Debugging: Print response
    print("\n--- API Response ---")
    print(json.dumps(api_output, indent=4))

    print("\n--- Expected Output ---")
    print(json.dumps(expected_output, indent=4))

    # Compare peak values
    assert api_output["peakEField"] == expected_output["peakEField"], "Mismatch in Peak E-Field"
    assert api_output["peakTime"] == expected_output["peakTime"], "Mismatch in Peak Time"

    # Compare time-series data
    assert len(api_output["timeSeriesData"]) == len(expected_output["timeSeriesData"]), "Mismatch in time series length"

    for api_point, expected_point in zip(api_output["timeSeriesData"], expected_output["timeSeriesData"]):
        assert api_point["time"] == expected_point["time"], f"Mismatch in time at {api_point['time']}"
        assert api_point["eField"] == expected_point["eField"], f"Mismatch in E-Field at time {api_point['time']}"

    print("✅ Test passed: API output matches expected results")

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_emp.py"])
