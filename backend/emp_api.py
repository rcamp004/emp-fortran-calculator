import binascii
from fastapi import FastAPI, HTTPException
import json
import os
from pydantic import BaseModel
import re
import shutil
import subprocess
import traceback
import tempfile

app = FastAPI(title="EMP Backend API", version="1.0.0", description="API for EMP Fortran Calculator")

# Input data model
class EMPInput(BaseModel):
    x: float
    y: float
    z: float
    hob: float
    gammaYield: float
    bField: float
    bAngle: float
    nSteps: int
    outputControl: int
    ap: float
    bp: float
    rnp: float
    top: float


# Response data model
class EMPOutput(BaseModel):
    peakEField: float
    peakTime: float
    timeSeriesData: list

@app.post("/run", response_model=EMPOutput)
def run_emp_calc(data: EMPInput, input_file: str = None):
    print("\n--- Received Input ---")
    print(data.dict())

    try:
        if input_file:
            input_file_path = input_file
            print(f"/nUsing provided input file: {input_file_path}")
        else:
            # ----------------------
            # Validate gammaYield
            # ----------------------
            if data.gammaYield == 0.0:
                raise HTTPException(status_code=400, detail="Gamma yield cannot be zero. Please provide a non-zero value.")


            # ----------------------
            # ETL: Create temporary IN2x.txt-like file
            # ----------------------
            input_text = (
                f"{data.x:>10.1f}{data.y:>10.1f}{data.z:>10.1f}{data.hob:>10.1f}{data.gammaYield:>10.3f}"
                f"{data.bField:>10.5f}{data.bAngle:>10.1f}{data.nSteps:>10}{data.outputControl:>10}\n"
                f"020\n"
                f"{data.ap:>10.1f}{data.bp:>10.2f}{data.rnp:>10.5f}{data.top:>10.2f}\n"
            )
            print("DEBUG: " + repr(input_text))
            # Create temp file for input
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, dir='/tmp', suffix='.txt') as temp_input:
                temp_input.write(input_text)
                temp_input_path = temp_input.name
                shutil.copy(temp_input.name, "temp_file_input.txt") # Save a copy to hexdump in the shell later to compare against original 

            print(f"Generated temp input file: {temp_input_path}")

            # Debugging: Print the input file content
            with open(temp_input_path, 'r') as f:
                print("\nDEBUG: Input File Content")
                print(f.read())
            
            # After writing the temp file
            with open(temp_input_path, "rb") as f:
                hex_dump = binascii.hexlify(f.read()).decode("utf-8")

            # Save the hex dump to another file
            hex_dump_path = f"{temp_input_path}_hex.txt"
            with open(hex_dump_path, "w") as hex_file:
                hex_file.write(hex_dump)

            print(f"Hex dump saved to: {hex_dump_path}")

        # ----------------------
        # Run the Fortran executable with this file as stdin
        # ----------------------
        process = subprocess.run(
            ['./run_emp_calc.sh'],
            stdin=open(temp_input_path, 'r'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # ----------------------
        # Handle execution errors
        # ----------------------
        if process.returncode != 0:
            print("Fortran STDERR:", process.stderr)
            raise HTTPException(status_code=500, detail=f"Execution failed: {process.stderr}")

        output = process.stdout
        print("Fortran STDOUT:", output)

        # ----------------------
        # DEBUGGING: PRINT RAW FORTRAN OUTPUT
        # ----------------------
        print("\nDEBUG: Raw Fortran Output (Before Parsing)")
        print(output)
        print("=" * 80)

        # ----------------------
        # Parse Fortran output (same as before)
        # ----------------------
        peak_efield = None
        peak_time = None
        time_series = []

        for line in output.splitlines():
            if "PEAK EFIELD AT TARGET IS" in line:
                peak_efield = float(line.split()[6])
            if "PEAK OCCURRED AT" in line:
                peak_time = float(line.split()[3])
            
            # Extract time and E-field values
            # Use regex to extract numerical values from the "TIME =" lines
            match = re.search(r"TIME =\s+([\d\.]+)\s+SHAKES\s+E\(T,RMAX\) =\s+([\d\.E+-]+)", line)
            if match:
                time_value = float(match.group(1))  # Extract TIME value
                e_field_value = float(match.group(2))  # Extract E(T,RMAX) value

                time_series.append({"time": time_value, "eField": e_field_value})

        # Before returning the response, add:
        response_dict = {
            "peakEField": peak_efield,
            "peakTime": peak_time,
            "timeSeriesData": time_series
            }
        print("\nDEBUG: API Response JSON:")
        print(json.dumps(response_dict, indent=4))

#         # Verify time_series_data is actually getting data
#         print("\nDEBUG: time_series_data:")
#         print(time_series[:5])

        return response_dict

    except Exception as e:
        print(traceback.format_exc())  # Full traceback for debugging
        raise HTTPException(status_code=500, detail=str(e))

