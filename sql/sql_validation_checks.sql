USE urban_pulse_db;

DESCRIBE service_requests;
SELECT COUNT(*) AS total_records,
       COUNT(DISTINCT unique_key) AS distinct_ids
FROM service_requests;
SELECT
    SUM(created_date IS NULL) AS missing_created_date,
    SUM(closed_date IS NULL) AS missing_closed_date,
    SUM(due_date IS NULL) AS missing_due_date,
    SUM(latitude IS NULL) AS missing_latitude,
    SUM(longitude IS NULL) AS missing_longitude,
    SUM(resolution_hours IS NULL) AS missing_resolution_hours
FROM service_requests;

SELECT is_closed,COUNT(*) AS total_requests
FROM service_requests
GROUP BY is_closed
ORDER BY is_closed;

SELECT
    COUNT(resolution_hours) AS valid_resolution_records,
    SUM(resolution_hours IS NULL) AS missing_resolution_records,
    MIN(resolution_hours) AS minimum_resolution_hours,
    MAX(resolution_hours) AS maximum_resolution_hours
FROM service_requests;

SELECT
    SUM(invalid_closure_date_flag = 1) AS invalid_closure_dates,
    SUM(invalid_due_date_flag = 1) AS invalid_due_dates,
    SUM(invalid_latitude_flag = 1) AS invalid_latitudes,
    SUM(invalid_longitude_flag = 1) AS invalid_longitudes
FROM service_requests;