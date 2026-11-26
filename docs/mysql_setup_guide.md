
# URBAN PULSE – MySQL Setup Guide

## 1. Introduction

In this project, I used MySQL to store the cleaned NYC 311 complaint data. Python is used to prepare and analyse the data, while MySQL helps store the records and perform SQL queries.

The database is connected to the Streamlit dashboard to display complaint statistics and analysis results.

## 2. Software Requirements

The following software and libraries are used in this project:

- Python
- MySQL Server 8.0
- Visual Studio Code
- Pandas
- SQLAlchemy / MySQL database connector (as configured in the project)
- Streamlit
- Python dotenv

## 3. Database Details

The project uses the following database:

| Item | Name |
|---|---|
| Database | urban_pulse_db |
| Main Table | service_requests |
| Database Server | MySQL |
| Data Source | NYC 311 Service Requests |

The cleaned complaint records are stored in the service_requests table.

## 4. Database Connection

Python connects to MySQL using the database connection settings stored in the project's `.env` file.

The `.env` file contains the database configuration, such as:

- Database host
- Database port
- Database name
- MySQL username
- MySQL password

The password is kept outside the shared source code to avoid exposing sensitive information.

Do not upload the `.env` file to GitHub.

## 5. Steps to Run the Project

Follow these steps to run URBAN PULSE on a Windows computer.

### Step 1: Start MySQL Server

Make sure the MySQL Server service is running.

### Step 2: Open the Project

Open the URBAN PULSE project folder in Visual Studio Code.

### Step 3: Activate the Virtual Environment

Open the VS Code terminal and run:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 4: Install Required Libraries

If the required libraries are not installed, run:

```powershell
pip install -r requirements.txt
```

### Step 5: Check Database Configuration

Make sure the `.env` file is present in the project root and contains the correct MySQL connection details.

### Step 6: Start the Dashboard

Run the following command from the project root folder:

```powershell
streamlit run dashboard/app.py
```

The Streamlit application will open in the browser.

Local dashboard address:

http://localhost:8501

## 6. Dashboard and Database Connection

When the dashboard starts, the application uses the configured database connection to retrieve complaint records.

The retrieved data is used to display:

- Total complaint volume
- Complaint closure rate
- Open complaints
- Median resolution time
- Complaints taking more than 72 hours
- Detailed complaint analysis and visualizations

## 7. Important Notes

- MySQL Server must be running before starting the dashboard.
- The database and service_requests table must already exist.
- The `.env` file must contain valid database connection settings.
- The cleaned dataset must be loaded into MySQL before running the dashboard.
- Database passwords should never be shared publicly.

## 8. Conclusion

MySQL provides the storage layer for the URBAN PULSE project. By connecting Python, MySQL, and Streamlit, I developed an application that stores complaint records and presents the analysis through an interactive dashboard.
