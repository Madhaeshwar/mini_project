
# URBAN PULSE – Final Findings Report

## 1. Introduction

URBAN PULSE is a data analytics project developed using NYC 311 Service Request data. The main aim of this project is to understand the types of complaints reported by citizens, identify complaint patterns, compare agency workloads, and analyse the time taken to close complaints.

For this project, I collected 100,000 records from the NYC Open Data API. I used Python for data cleaning and analysis, MySQL for storing and querying the data, and Streamlit to develop an interactive dashboard.

## 2. Dataset Overview

The dataset contains citizen complaints reported across the five boroughs of New York City.

- Total records: 100,000
- Unique request IDs: 100,000
- Selected original columns: 13
- Data source: NYC Open Data – 311 Service Requests
- Database: MySQL
- Dashboard: Streamlit

After extracting the data, I performed data cleaning, validation, statistical analysis, and feature engineering.

## 3. Key Dashboard Findings

The dashboard displays five important KPIs to provide an overview of complaint handling.

| KPI | Project Result |
|---|---:|
| Total Requests | 100,000 |
| Closure Rate | 99.04% |
| Open Requests | 959 |
| Median Resolution Time | 22.12 hours |
| Complaints Taking Over 72 Hours | 27.71% |

The results show that most recorded complaints have a closure date. However, some complaints take considerably longer to close.

The median resolution time was approximately 22.12 hours, meaning that half of the valid resolution durations were at or below this value.

## 4. Complaint Distribution Across Boroughs

I analysed the number of complaints reported in each borough.

| Borough | Number of Complaints |
|---|---:|
| Brooklyn | 31,088 |
| Queens | 25,718 |
| Manhattan | 20,055 |
| Bronx | 16,796 |
| Staten Island | 5,316 |

Brooklyn recorded the highest number of complaints in this dataset, followed by Queens and Manhattan. Staten Island had the lowest recorded complaint count.

These figures represent the selected dataset and should not be interpreted as a complete measure of the actual problems experienced by residents.

## 5. Complaint Resolution Time Analysis

One of the important parts of this project was understanding how long agencies took to close complaints.

The following statistical values were obtained:

| Measurement | Result |
|---|---:|
| Valid Resolution Records | 98,174 |
| Mean Resolution Time | 824.09 hours |
| Median Resolution Time | 22.12 hours |
| Minimum | 0 hours |
| Maximum | 58,542.33 hours |
| Standard Deviation | 4,614.33 hours |

There is a large difference between the mean and median resolution times.

This indicates that the resolution-time distribution is strongly affected by a smaller number of complaints that took a very long time to close.

## 6. Outlier Analysis

I used the Interquartile Range (IQR) method to identify unusually long resolution durations.

The calculated upper outlier limit was approximately 214.89 hours.

The analysis identified:

- Upper outliers: 14,592
- Lower outliers: 0
- Outlier percentage among valid resolution records: approximately 14.86%

I did not remove these records because long resolution times may represent genuine delays in complaint handling.

Instead, I identified the outliers so they could be investigated separately.

## 7. Analyst Investigations

I completed 15 investigations as part of the project.

The investigations covered the following areas:

1. Total complaint volume – Examined the overall number of citizen requests.
2. Top 10 complaint categories – Identified the most frequently reported complaint types.
3. Agency workload – Compared the number of complaints handled by different agencies.
4. Borough analysis – Studied complaint distribution across the five boroughs.
5. Monthly complaint trend – Examined how complaint volume changed over time.
6. Weekday and hourly demand – Analysed when complaints were registered.
7. Request status distribution – Examined the recorded status of complaints.
8. Resolution time statistics – Calculated descriptive statistics for valid resolution durations.
9. Resolution by complaint category – Compared median resolution times across complaint types.
10. Resolution by agency – Compared median resolution times across agencies.
11. Outlier investigation – Used the IQR method to identify unusually long resolution times.
12. Skewness and distribution – Examined the shape of the resolution-time distribution.
13. Geographic complaint concentration – Explored complaint locations using available coordinates.
14. Agency closure rate – Compared recorded closure rates across agencies.
15. High-volume and long-resolution complaints – Investigated complaint categories with both high demand and longer median resolution times.

These investigations helped explore different aspects of complaint demand and recorded resolution patterns.

## 8. Important Observations

From the overall analysis, I identified several important observations:

- Complaint records were not distributed equally across the five boroughs.
- Different agencies handled different volumes of complaints.
- Complaint demand could be explored by month, weekday, and hour.
- The resolution-time distribution was strongly right-skewed.
- The mean resolution time was much higher than the median because of unusually long resolution durations.
- Some complaint records contained missing or inconsistent date and location information.
- Geographic analysis was possible for records with usable coordinates.

## 9. Limitations

During the project, I identified a few limitations:

1. The analysis uses a selected sample of 100,000 records rather than every NYC 311 request.
2. Some records contain missing values, especially in due dates and location information.
3. Agency and complaint comparisons may be affected by differences in complaint complexity.
4. A recorded closure does not necessarily mean that the citizen was satisfied with the result.
5. Long resolution times may be genuine cases and should not automatically be treated as incorrect data.
6. The 72-hour threshold used in the dashboard is an analytical threshold selected for this project, not an officially verified service-level standard.

## 10. Conclusion

Through URBAN PULSE, I gained practical experience in collecting real-world data from an API, cleaning datasets using Python, performing statistical analysis, writing SQL queries, and developing an interactive Streamlit dashboard.

The project helped me understand how data analytics can be used to study citizen complaints, service demand, agency workload, and complaint resolution patterns.

Overall, URBAN PULSE provides an analytical view of NYC 311 service requests and demonstrates how different technologies can be combined to build an end-to-end data analytics project.
