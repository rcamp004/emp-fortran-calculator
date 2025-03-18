# EMP Fortran Calculator

## Overview
The **EMP Fortran Calculator** is a tool designed to run EMP (Electromagnetic Pulse) simulations using a Fortran-based computational model. This project provides a frontend UI for input and visualization, along with a backend API that processes the simulation using a Fortran executable.

## Features
- Streamlit-based **web UI** for user-friendly parameter input
- **FastAPI backend** to handle computation requests
- **Fortran-based numerical model** for EMP calculations
- **Interactive graphs** using Plotly for result visualization
- **Dockerized deployment** for easy setup and execution

## Project Structure
```
emp_calc_docker/
├── backend/            # Backend API service
│   ├── Dockerfile      # Backend Docker configuration
│   ├── emp_api.py      # FastAPI backend logic
│   ├── emp_calc.x      # Fortran compiled executable
│   ├── run_emp_calc.sh # Shell script to run the Fortran model
│   └── requirements.txt # Python dependencies
├── frontend/           # Frontend UI service
│   ├── Dockerfile      # Frontend Docker configuration
│   ├── emp_ui.py       # Streamlit-based UI
│   └── requirements.txt # Python dependencies
├── docker-compose.yml  # Docker Compose configuration
└── README.md           # Project documentation
```

## Installation & Usage
### **1. Prerequisites**
Ensure you have:
- **Docker** and **Docker Compose** installed
- A working **Fortran compiler** if modifying the core simulation

### **2. Clone the Repository**
```bash
git clone https://github.com/rcamp004/emp-fortran-calculator.git
cd emp-fortran-calculator
```

### **3. Build and Run the Containers**
```bash
docker-compose up --build
```
This starts both the **backend** and **frontend** services.

### **4. Access the UI**
Once running, visit:
```
http://localhost:8501
```

## API Endpoints
The backend runs on `http://localhost:8000` and provides the following API:
### **POST /run** (Run EMP Calculation)
**Request Body:**
```json
{
  "x": 0.0,
  "y": 0.0,
  "z": 0.0,
  "hob": 100,
  "gammaYield": 0.001,
  "bField": 0.00002,
  "bAngle": 20.0,
  "nSteps": 50,
  "outputControl": 0,
  "ap": 2.2,
  "bp": 0.25,
  "rnp": 5.62603,
  "top": 2.24
}
```

**Response:**
```json
{
  "peakEField": 1115.0,
  "peakTime": 9.0,
  "timeSeriesData": [
    { "time": 0.1, "eField": 0.04892 },
    { "time": 0.2, "eField": 0.09165 },
    ...
  ]
}
```

## Debugging
If needed, check logs using:
```bash
docker logs emp-backend-1
```

## Contribution
If you'd like to contribute:
1. Fork the repo
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit changes (`git commit -m "Added feature"`)
4. Push (`git push origin feature-branch`)
5. Open a **Pull Request**

## License
MIT License

## Contact
For any issues or discussions, open a GitHub issue or contact **rcamp004** on GitHub.
