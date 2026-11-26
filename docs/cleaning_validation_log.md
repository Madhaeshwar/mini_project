
# URBAN PULSE – Data Cleaning and Validation Log

## 1. Introduction

Before starting the analysis, I prepared the NYC 311 dataset to make it suitable for statistical analysis and dashboard development.

The original dataset contained 100,000 records. During the cleaning process, I checked the columns, data types, missing values, duplicate records, and date-related inconsistencies.

I also created additional columns that were useful for analysing complaint resolution time and reporting patterns.

## 2. Initial Dataset Inspection

First, I loaded the extracted CSV file into Python using Pandas and inspected its structure.

The initial dataset had the following details:

- Total records: 100,000
- Selected columns: 13
- Unique request IDs: 100,000
- Duplicate request IDs: 0

I checked the column names, data types, sample records, and missing values to understand the condition of the dataset before cleaning.

## 3. Data Cleaning Steps

### 3.1 Date Conversion

The created_date, closed_date, and due_date columns were converted into datetime format.

This was necessary to calculate complaint resolution duration and perform time-based analysis.

Missing date values were preserved instead of replacing them with estimated dates.

### 3.2 Text Cleaning

I cleaned the text columns by removing unnecessary whitespace and standardising text values where appropriate.

This helped maintain consistency when grouping complaints by agency, borough, category, and other fields.

### 3.3 Numeric and Coordinate Conversion

Latitude and longitude values were checked and converted into numeric format.

The incident_zip column was stored as text because ZIP codes are identifiers rather than values used for mathematical calculations.

Invalid coordinate values were checked during the cleaning process.

### 3.4 Duplicate Record Checking

I checked the unique_key column to identify duplicate complaint records.

The dataset contained 100,000 records and 100,000 unique request IDs.

No duplicate request IDs were found.

### 3.5 Handling Missing Values

Some columns contained missing values. I did not replace all missing values because certain missing values represent genuine situations.

For example, a complaint without a closed_date may still be open. Therefore, assigning an estimated closure date could produce incorrect resolution-time calculations.

The missing values were preserved where appropriate.

## 4. Missing Value Summary

The following missing values remained after cleaning:

| Column Name | Missing Records |
|---|---:|
| closed_date | 959 |
| due_date | 99,116 |
| latitude | 3,917 |
| longitude | 3,917 |
| resolution_hours | 1,826 |

The due_date column had a large number of missing values. These were retained because the project does not assume that every complaint has a recorded due date.

## 5. Date Validation

I also checked whether the dates were logically consistent.

The following issues were identified:

| Validation Check | Records Found |
|---|---:|
| Closure date earlier than creation date | 867 |
| Due date earlier than creation date | 16 |

These records were identified using data-quality flags.

I did not silently change the original dates because the incorrect values needed to remain identifiable for further investigation.

## 6. Feature Engineering

After cleaning the dataset, I created additional columns to support the analysis.

- resolution_hours: Calculates the time between complaint creation and closure.
- is_closed: Identifies complaints with a recorded closure date.
- created_year: Extracts the year from the creation date.
- created_month: Extracts the month from the creation date.
- created_weekday: Identifies the weekday of complaint creation.
- created_hour: Extracts the hour of complaint creation.

I also created flags to identify invalid closure dates, invalid due dates, and invalid coordinate values.

## 7. Outlier Detection

I used the Interquartile Range (IQR) method to identify unusually long complaint resolution times.

The following values were calculated:

| Measurement | Result |
|---|---:|
| Q1 | 2.65 hours |
| Q3 | 87.55 hours |
| IQR | 84.90 hours |
| Lower limit | -124.69 hours |
| Upper limit | 214.89 hours |
| Upper outliers | 14,592 |
| Lower outliers | 0 |

The outliers were identified and reviewed rather than automatically removed.

I preserved the original resolution times because some complaints may genuinely take a long time to resolve.

## 8. Validation Results

After the cleaning process, I checked the dataset again.

The main validation results were:

- The dataset retained 100,000 records.
- All request IDs were unique.
- No duplicate request IDs were found.
- Date columns were converted into datetime format.
- Text and ZIP code values were cleaned.
- Coordinate values were checked.
- Missing values were preserved where meaningful.
- Invalid date combinations were identified using flags.
- Additional columns were created for statistical and time-based analysis.

## 9. Conclusion

The cleaning process helped prepare the NYC 311 dataset for further analysis.

Instead of deleting records or filling every missing value, I tried to preserve the original information wherever possible.

The prepared dataset was then used for statistical analysis, SQL investigations, and the URBAN PULSE Streamlit dashboard.
