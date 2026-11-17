USE urban_pulse_db;
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT unique_key) AS distinct_requests
FROM service_requests;
SELECT
    complaint_type,
    COUNT(*) AS total_complaints
FROM service_requests
GROUP BY complaint_type
ORDER BY total_complaints DESC
LIMIT 10;
-- Investigation 3: Agency Workload Distribution

SELECT
    agency,
    COUNT(*) AS total_complaints
FROM service_requests
GROUP BY agency
ORDER BY total_complaints DESC;

-- Investigation 4: Request Volume by Borough

SELECT
    borough,
    COUNT(*) AS total_complaints
FROM service_requests
GROUP BY borough
ORDER BY total_complaints DESC;

SELECT
    DATE_FORMAT(created_date, '%Y-%m') AS request_month,
    COUNT(*) AS total_complaints
FROM service_requests
WHERE created_date IS NOT NULL
GROUP BY DATE_FORMAT(created_date, '%Y-%m')
ORDER BY request_month;

-- Investigation 6A: Request demand by weekday

SELECT
    created_weekday,
    COUNT(*) AS total_complaints
FROM service_requests
GROUP BY created_weekday
ORDER BY total_complaints DESC;

-- Investigation 6B: Request demand by hour

SELECT
    created_hour,
    COUNT(*) AS total_complaints
FROM service_requests
GROUP BY created_hour
ORDER BY created_hour;

-- Investigation 7: Distribution of recorded request statuses

SELECT
    status,
    COUNT(*) AS total_complaints
FROM service_requests
GROUP BY status
ORDER BY total_complaints DESC;

-- Investigation 8: Descriptive statistics for valid resolution durations

SELECT
    COUNT(resolution_hours) AS valid_records,
    AVG(resolution_hours) AS average_hours,
    MIN(resolution_hours) AS minimum_hours,
    MAX(resolution_hours) AS maximum_hours,
    STDDEV_POP(resolution_hours) AS standard_deviation,
    VAR_POP(resolution_hours) AS variance
FROM service_requests
WHERE resolution_hours IS NOT NULL;

-- Investigation 9: Median resolution duration by complaint category

SELECT
    complaint_type,
    COUNT(resolution_hours) AS valid_records,
    AVG(resolution_hours) AS average_hours
FROM service_requests
WHERE resolution_hours IS NOT NULL
GROUP BY complaint_type
ORDER BY average_hours DESC;

-- Investigation 9: Median resolution duration by complaint category

-- Objective:
-- Calculate the median resolution time for each complaint category.
WITH ranked_resolution AS (
    SELECT
        complaint_type,
        resolution_hours,
        ROW_NUMBER() OVER (
            PARTITION BY complaint_type
            ORDER BY resolution_hours
        ) AS row_num,
        COUNT(*) OVER (
            PARTITION BY complaint_type
        ) AS category_count
    FROM service_requests
    WHERE resolution_hours IS NOT NULL
)

SELECT
    complaint_type,
    MAX(category_count) AS valid_records,
    AVG(resolution_hours) AS median_resolution_hours
FROM ranked_resolution
WHERE row_num IN (
    FLOOR((category_count + 1) / 2),
    FLOOR((category_count + 2) / 2)
)
GROUP BY complaint_type
ORDER BY median_resolution_hours DESC;

-- Investigation 10: Median resolution duration by agency

WITH ranked_resolution AS (
    SELECT
        agency,
        resolution_hours,

        ROW_NUMBER() OVER (
            PARTITION BY agency
            ORDER BY resolution_hours
        ) AS row_num,

        COUNT(*) OVER (
            PARTITION BY agency
        ) AS agency_count

    FROM service_requests
    WHERE resolution_hours IS NOT NULL
      AND agency IS NOT NULL
)

SELECT
    agency,
    MAX(agency_count) AS valid_records,
    AVG(resolution_hours) AS median_resolution_hours

FROM ranked_resolution

WHERE row_num IN (
    FLOOR((agency_count + 1) / 2),
    FLOOR((agency_count + 2) / 2)
)

GROUP BY agency
ORDER BY median_resolution_hours DESC;


-- Investigation 11: Identify resolution-time outliers using IQR

WITH quartiles AS (
    SELECT
        resolution_hours,

        NTILE(4) OVER (
            ORDER BY resolution_hours
        ) AS quartile_group

    FROM service_requests
    WHERE resolution_hours IS NOT NULL
),

quartile_values AS (
    SELECT
        MAX(
            CASE
                WHEN quartile_group = 1
                THEN resolution_hours
            END
        ) AS q1,

        MAX(
            CASE
                WHEN quartile_group = 3
                THEN resolution_hours
            END
        ) AS q3

    FROM quartiles
)

SELECT
    q1,
    q3,
    (q3 - q1) AS iqr,
    (q1 - 1.5 * (q3 - q1)) AS lower_limit,
    (q3 + 1.5 * (q3 - q1)) AS upper_limit
FROM quartile_values;

-- Investigation 11: Count resolution-time outliers

WITH quartiles AS (
    SELECT
        resolution_hours,

        NTILE(4) OVER (
            ORDER BY resolution_hours
        ) AS quartile_group

    FROM service_requests
    WHERE resolution_hours IS NOT NULL
),

quartile_values AS (
    SELECT
        MAX(
            CASE
                WHEN quartile_group = 1
                THEN resolution_hours
            END
        ) AS q1,

        MAX(
            CASE
                WHEN quartile_group = 3
                THEN resolution_hours
            END
        ) AS q3

    FROM quartiles
),

limits AS (
    SELECT
        q1 - 1.5 * (q3 - q1) AS lower_limit,
        q3 + 1.5 * (q3 - q1) AS upper_limit
    FROM quartile_values
)

SELECT
    COUNT(*) AS total_valid_records,

    SUM(
        CASE
            WHEN resolution_hours < lower_limit
            THEN 1 ELSE 0
        END
    ) AS lower_outliers,

    SUM(
        CASE
            WHEN resolution_hours > upper_limit
            THEN 1 ELSE 0
        END
    ) AS upper_outliers,

    SUM(
        CASE
            WHEN resolution_hours < lower_limit
              OR resolution_hours > upper_limit
            THEN 1 ELSE 0
        END
    ) AS total_outliers

FROM service_requests
CROSS JOIN limits
WHERE resolution_hours IS NOT NULL;

-- Investigation 12: Resolution-time distribution

SELECT
    COUNT(resolution_hours) AS valid_records,
    AVG(resolution_hours) AS mean_hours,
    MIN(resolution_hours) AS minimum_hours,
    MAX(resolution_hours) AS maximum_hours,
    STDDEV_POP(resolution_hours) AS standard_deviation,
    VAR_POP(resolution_hours) AS variance

FROM service_requests
WHERE resolution_hours IS NOT NULL;

-- Investigation 13: Geographic complaint concentration by borough

SELECT
    borough,
    COUNT(*) AS total_complaints,
    COUNT(latitude) AS records_with_latitude,
    COUNT(longitude) AS records_with_longitude,
    COUNT(
        CASE
            WHEN latitude IS NOT NULL
             AND longitude IS NOT NULL
            THEN 1
        END
    ) AS records_with_coordinates

FROM service_requests

GROUP BY borough
ORDER BY total_complaints DESC;

-- Investigation 13: Overall geographic coordinate availability

SELECT
    COUNT(*) AS total_records,

    COUNT(
        CASE
            WHEN latitude IS NOT NULL
             AND longitude IS NOT NULL
            THEN 1
        END
    ) AS records_with_coordinates,

    COUNT(
        CASE
            WHEN latitude IS NULL
              OR longitude IS NULL
            THEN 1
        END
    ) AS records_without_coordinates

FROM service_requests;

-- Investigation 14: Recorded closure rate by agency

SELECT
    agency,

    COUNT(*) AS total_requests,

    SUM(is_closed) AS closed_requests,

    COUNT(*) - SUM(is_closed) AS not_closed_requests,

    ROUND(
        (SUM(is_closed) / COUNT(*)) * 100,
        2
    ) AS closure_rate_percentage

FROM service_requests

WHERE agency IS NOT NULL

GROUP BY agency

ORDER BY closure_rate_percentage DESC;

-- Investigation 15: High-volume complaints with long resolution times

WITH ranked_complaints AS (
    SELECT
        complaint_type,
        resolution_hours,

        ROW_NUMBER() OVER (
            PARTITION BY complaint_type
            ORDER BY resolution_hours
        ) AS row_num,

        COUNT(*) OVER (
            PARTITION BY complaint_type
        ) AS category_count

    FROM service_requests
    WHERE resolution_hours IS NOT NULL
      AND complaint_type IS NOT NULL
),

category_medians AS (
    SELECT
        complaint_type,
        MAX(category_count) AS valid_records,
        AVG(resolution_hours) AS median_resolution_hours

    FROM ranked_complaints

    WHERE row_num IN (
        FLOOR((category_count + 1) / 2),
        FLOOR((category_count + 2) / 2)
    )

    GROUP BY complaint_type
),

category_volumes AS (
    SELECT
        complaint_type,
        COUNT(*) AS total_complaints

    FROM service_requests
    WHERE complaint_type IS NOT NULL

    GROUP BY complaint_type
)

SELECT
    v.complaint_type,
    v.total_complaints,
    m.median_resolution_hours

FROM category_volumes v

JOIN category_medians m
    ON v.complaint_type = m.complaint_type

ORDER BY
    v.total_complaints DESC,
    m.median_resolution_hours DESC

LIMIT 20;