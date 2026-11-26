
# URBAN PULSE – Data Dictionary

## 1. Introduction

URBAN PULSE is a data analytics project based on NYC 311 service requests. The dataset contains complaints reported by citizens in New York City.

For this project, I collected 100,000 records from the NYC Open Data API and selected 13 important columns for further analysis.

This data dictionary explains the columns used in the project, what information they contain, and how they are useful for the analysis.

## 2. Details of the Dataset

- Dataset: NYC 311 Service Requests
- Data Source: NYC Open Data
- Total Records: 100,000
- Selected Columns: 13
- Format: CSV
- Main Purpose: To study complaint patterns and the time taken to close complaints.

## 3. Description of the Original Columns

The following columns were selected from the original dataset.

| Column Name | Description | Data Type |
|---|---|---|
| unique_key | A unique number assigned to each complaint. | Integer |
| created_date | The date and time when the complaint was registered. | Datetime |
| closed_date | The date and time when the complaint was closed. | Datetime |
| due_date | The expected date for completing the complaint. | Datetime |
| agency | The department responsible for handling the complaint. | String |
| complaint_type | The main category of the reported complaint. | String |
| borough | The New York City borough where the complaint was reported. | String |
| status | The recorded status of the complaint. | String |
| latitude | The latitude coordinate of the complaint location. | Float |
| longitude | The longitude coordinate of the complaint location. | Float |
| incident_zip | The ZIP code of the complaint location. | String |
| location_type | The type of location associated with the complaint. | String |
| descriptor | Additional information describing the complaint. | String |

## 4. Additional Columns Created During Data Preparation

Some additional columns were created to make the analysis easier.

| Column Name | Purpose |
|---|---|
| resolution_hours | Calculates how many hours it took to close a complaint. |
| is_closed | Indicates whether a complaint has a recorded closure date. |
| created_year | Stores the year in which the complaint was created. |
| created_month | Stores the month in which the complaint was created. |
| created_weekday | Identifies the day of the week when the complaint was created. |
| created_hour | Stores the hour when the complaint was registered. |
| invalid_closure_date_flag | Identifies records where the closure date is earlier than the creation date. |
| invalid_due_date_flag | Identifies records where the due date is earlier than the creation date. |
| invalid_latitude_flag | Helps identify invalid latitude values. |
| invalid_longitude_flag | Helps identify invalid longitude values. |

These additional columns helped me perform time-based analysis, calculate complaint resolution duration, and identify possible data quality problems.

## 5. Missing Values in the Dataset

During data cleaning, I found that some columns contained missing values.

| Column Name | Number of Missing Values |
|---|---:|
| closed_date | 959 |
| due_date | 99,116 |
| latitude | 3,917 |
| longitude | 3,917 |
| resolution_hours | 1,826 |

I decided not to fill all missing values with artificial data. For example, a complaint without a closure date may still be open, so filling it with an estimated date could affect the analysis.

Missing values were preserved wherever the information was not available.

## 6. Data Quality Checks

After preparing the dataset, I performed several checks to understand its quality.

- The dataset contains 100,000 records.
- All 100,000 request IDs are unique.
- No duplicate request IDs were found.
- 867 records had closure dates earlier than their creation dates.
- 16 records had due dates earlier than their creation dates.
- No invalid latitude or longitude values were identified in the coordinate checks.

Records with inconsistent dates were identified using separate flags instead of silently changing their original values.

## 7. How the Columns Are Used in the Project

Each group of columns helps answer a different question.

- Complaint information is used to identify the most frequently reported problems.
- Agency and borough information helps compare complaint distribution across departments and locations.
- Creation dates help identify monthly, weekday, and hourly complaint patterns.
- Closure dates help calculate the time taken to resolve complaints.
- Latitude and longitude help explore the geographic distribution of complaints.

## 8. Conclusion

Preparing this data dictionary helped me understand the structure of the NYC 311 dataset and the purpose of each selected column.

It also provides a clear reference for the data preparation, SQL analysis, and Streamlit dashboard developed as part of the URBAN PULSE project.
