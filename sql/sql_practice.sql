USE urban_pulse_db;

SELECT unique_key,complaint_type,borough,status
FROM service_requests
WHERE borough = 'BROOKLYN'
LIMIT 10;

SELECT borough,COUNT(*) AS total_complaints
FROM service_requests
GROUP BY borough
ORDER BY total_complaints DESC;
SELECT COUNT(resolution_hours) AS valid_records,
    ROUND(AVG(resolution_hours), 2) AS average_hours,
    ROUND(MIN(resolution_hours), 2) AS minimum_hours,
    ROUND(MAX(resolution_hours), 2) AS maximum_hours
FROM service_requests;
SELECT unique_key,complaint_type,resolution_hours
FROM service_requests
WHERE resolution_hours IS NOT NULL
ORDER BY resolution_hours DESC
LIMIT 10;
-- 5. Count complaints by year

SELECT
    YEAR(created_date) AS request_year,
    COUNT(*) AS total_complaints
FROM service_requests
GROUP BY YEAR(created_date)
ORDER BY request_year;

SELECT MONTH(created_date) AS request_month,COUNT(*) AS total_complaints
FROM service_requests
GROUP BY MONTH(created_date)
ORDER BY request_month;

-- 7. Classify resolution durations

SELECT
    CASE
        WHEN resolution_hours <= 24 THEN 'Within 24 Hours'
        WHEN resolution_hours <= 72 THEN '24-72 Hours'
        ELSE 'Above 72 Hours'
    END AS resolution_category,
    COUNT(*) AS total_complaints
FROM service_requests
WHERE resolution_hours IS NOT NULL
GROUP BY resolution_category
ORDER BY total_complaints DESC;

-- 8. Find boroughs with more than 20000 complaints

SELECT
    borough,
    COUNT(*) AS total_complaints
FROM service_requests
GROUP BY borough
HAVING COUNT(*) > 20000
ORDER BY total_complaints DESC;

SHOW TABLES;

SELECT DISTINCT complaint_type
FROM service_requests
ORDER BY complaint_type;

-- 10. Count unique complaint categories

SELECT
    COUNT(DISTINCT complaint_type) AS unique_categories
FROM service_requests;

SELECT
    DATE_FORMAT(created_date, '%Y-%m') AS request_month,
    COUNT(*) AS total_complaints
FROM service_requests
GROUP BY DATE_FORMAT(created_date, '%Y-%m')
ORDER BY request_month;

-- 12. Count closed and open requests using conditional aggregation

SELECT
    SUM(CASE WHEN is_closed = 1 THEN 1 ELSE 0 END) AS closed_requests,
    SUM(CASE WHEN is_closed = 0 THEN 1 ELSE 0 END) AS open_requests
FROM service_requests;