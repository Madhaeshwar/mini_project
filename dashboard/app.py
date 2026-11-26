import os
import re
from pathlib import Path

import mysql.connector
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

st.set_page_config(page_title="URBAN PULSE", page_icon="🏙️", layout="wide")

# --------------------------------------------------
# Setup and helpers
# --------------------------------------------------
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
db_password = os.getenv("URBAN_PULSE_DB_PASSWORD")
if not db_password:
    st.error("Database password not found. Check your .env file.")
    st.stop()

TR = "Total Requests"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
VALID = "resolution_hours IS NOT NULL AND resolution_hours >= 0"


def query(sql, params=None):
    """Run one query and return all rows; the connection is always closed."""
    conn = mysql.connector.connect(
        host="localhost", user="root", password=db_password, database="urban_pulse_db"
    )
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def frame(rows, cols):
    """Rows -> DataFrame, converting Decimal columns to float."""
    df = pd.DataFrame(rows, columns=cols)
    for c in cols[1:]:
        if df[c].dtype == object:
            df[c] = df[c].astype(float)
    return df


def pct(a, b):
    return f"{a / b:.1%}" if b else "N/A"


def insights(*points):
    """Show findings in short, easy-to-read message boxes."""
    st.subheader("📌 Key Insights")
    st.caption("A simple explanation of what the chart is showing.")

    for number, point in enumerate(points, start=1):
        st.markdown(f"**{number}.** {point}")


def median_sql(group=None):
    """Median resolution hours (overall, or per group column) + valid record count."""
    part = f"PARTITION BY {group}" if group else ""
    sel = f"{group}, " if group else ""
    cond = f"{group} IS NOT NULL AND " if group else ""
    tail = f"GROUP BY {group} ORDER BY 2 DESC" if group else ""
    return f"""
        WITH r AS (
            SELECT {sel}resolution_hours AS h,
                   ROW_NUMBER() OVER ({part} ORDER BY resolution_hours) AS rn,
                   COUNT(*) OVER ({part}) AS n
            FROM service_requests
            WHERE {cond}{VALID}
        )
        SELECT {sel}ROUND(AVG(h), 2), MAX(n)
        FROM r
        WHERE rn IN (FLOOR((n + 1) / 2), FLOOR((n + 2) / 2))
        {tail}
    """


# --------------------------------------------------
# Dashboard Filters
# --------------------------------------------------
# These option queries use the full dataset so the available choices do not
# disappear when a filter is selected.
date_bounds = query("""
    SELECT MIN(DATE(created_date)), MAX(DATE(created_date))
    FROM service_requests
""")[0]

min_date, max_date = date_bounds
if min_date is None or max_date is None:
    st.error("No created dates were found in the service_requests table.")
    st.stop()

borough_options = [
    row[0] for row in query("""
        SELECT DISTINCT borough
        FROM service_requests
        WHERE borough IS NOT NULL
        ORDER BY borough
    """)
]

complaint_options = [
    row[0] for row in query("""
        SELECT DISTINCT complaint_type
        FROM service_requests
        WHERE complaint_type IS NOT NULL
        ORDER BY complaint_type
    """)
]

st.sidebar.title("URBAN PULSE")
st.sidebar.header("Dashboard Filters")

date_range = st.sidebar.date_input(
    "Created Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

selected_boroughs = st.sidebar.multiselect(
    "Select Borough",
    options=borough_options,
)

selected_complaints = st.sidebar.multiselect(
    "Select Complaint Type",
    options=complaint_options,
)

# Streamlit may return one date while the user is still choosing a range.
if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_range

filter_conditions = ["DATE(created_date) BETWEEN %s AND %s"]
filter_params = [start_date, end_date]

if selected_boroughs:
    placeholders = ", ".join(["%s"] * len(selected_boroughs))
    filter_conditions.append(f"borough IN ({placeholders})")
    filter_params.extend(selected_boroughs)

if selected_complaints:
    placeholders = ", ".join(["%s"] * len(selected_complaints))
    filter_conditions.append(f"complaint_type IN ({placeholders})")
    filter_params.extend(selected_complaints)

FILTER_WHERE = " AND ".join(filter_conditions)


def filtered_query(sql, params=None):
    """Run an analysis query against rows matching the dashboard filters."""
    match = re.search(r"\bFROM\s+service_requests\b", sql, flags=re.IGNORECASE)
    if not match:
        raise ValueError("The analysis SQL must read from service_requests.")

    # Keep any query parameters that appear before FROM in their original
    # position (for example, the two parameters used in the skewness query).
    params = tuple(params or ())
    params_before_from = sql[:match.start()].count("%s")
    ordered_params = (
        params[:params_before_from]
        + tuple(filter_params)
        + params[params_before_from:]
    )

    filtered_table = (
        "FROM (SELECT * FROM service_requests WHERE "
        + FILTER_WHERE
        + ") AS service_requests"
    )
    filtered_sql = re.sub(
        r"\bFROM\s+service_requests\b",
        lambda _: filtered_table,
        sql,
        count=1,
        flags=re.IGNORECASE,
    )
    return query(filtered_sql, ordered_params)


# --------------------------------------------------
# Headline KPIs
# --------------------------------------------------
try:
    row = filtered_query(f"""
    SELECT COUNT(DISTINCT unique_key),
           COUNT(DISTINCT CASE WHEN is_closed = 1 THEN unique_key END),
           COUNT(DISTINCT CASE WHEN is_closed = 0 THEN unique_key END),
           COUNT(DISTINCT CASE WHEN resolution_hours > 72 THEN unique_key END)
    FROM service_requests
""")[0]
    total, closed, open_, over_72 = (int(v or 0) for v in row)
    med = filtered_query(median_sql())[0][0]
    median_resolution = float(med) if med is not None else None
except mysql.connector.Error as error:
    st.error(f"Database operation failed: {error}")
    st.stop()

if total == 0:
    st.title("🏙️ URBAN PULSE")
    st.warning("No records match the selected filters. Please change the date range, borough, or complaint type.")
    st.stop()

st.title("🏙️ URBAN PULSE")
st.subheader("NYC 311 Citizen Complaint Analysis")
st.caption("Citizen complaints, agency workload, borough distribution and resolution time.")
st.divider()

st.header("📊 Dashboard — Five KPIs")
kpis = [
    ("Total Requests", f"{total:,}"),
    ("Recorded Closure", pct(closed, total)),
    ("Open Requests", f"{open_:,}"),
    ("Median Resolution", f"{median_resolution:,.1f} hrs" if median_resolution is not None else "N/A"),
    ("Over 72 Hours", pct(over_72, total)),
]
for col, (label, value) in zip(st.columns(5), kpis):
    col.metric(label, value)
st.caption("Closure is based on a recorded close date. It does not measure citizen satisfaction. The 72-hour cut-off is an example project threshold.")
st.divider()

# --------------------------------------------------
# Analyses (each one registers itself in ANALYSES)
# --------------------------------------------------
ANALYSES = {}


def analysis(name):
    def register(fn):
        ANALYSES[name] = fn
        return fn
    return register


@analysis("Total Complaint Volume")
def total_volume():
    unique, rows, first, last = filtered_query("""
        SELECT COUNT(DISTINCT unique_key), COUNT(*), MIN(created_date), MAX(created_date)
        FROM service_requests
    """)[0]
    days = max((last - first).days + 1, 1)
    st.metric("Total Unique Complaints", f"{unique:,}")
    insights(
        f"The dataset holds **{unique:,}** unique complaints from {first:%d %b %Y} to {last:%d %b %Y} ({days:,} days).",
        f"On average, about **{unique / days:,.0f} complaints were received each day**.",
        f"**{pct(closed, total)}** of requests are closed, leaving **{open_:,}** still open.",
        f"{rows - unique:,} duplicate rows were found on the complaint ID, so de-duplication is needed."
        if rows != unique else "Every complaint ID is unique, so the data is clean on this key.",
    )


@analysis("Top 10 Complaint Categories")
def top_categories():
    df = frame(filtered_query("""
        SELECT complaint_type, COUNT(*) FROM service_requests
        WHERE complaint_type IS NOT NULL GROUP BY complaint_type ORDER BY 2 DESC LIMIT 10
    """), ["Complaint Category", TR])
    st.bar_chart(df, x="Complaint Category", y=TR, horizontal=True)
    n, t = df["Complaint Category"], df[TR]
    insights(
        f"**{n[0]}** is the most reported issue with {t[0]:,} requests ({pct(t[0], total)} of all complaints).",
        f"The three most common complaint types account for **{pct(t[:3].sum(), total)}** of requests. The top ten account for **{pct(t.sum(), total)}**.",
        f"The most common complaint type was reported **{t[0] / t[1]:.1f} times** as often as the second most common type ({n[1]}).",
        f"The tenth category ({n.iloc[-1]}) received far fewer reports than the most common category.",
    )


@analysis("Agency Workload Distribution")
def agency_workload():
    df = frame(filtered_query("""
        SELECT agency, COUNT(*) FROM service_requests
        WHERE agency IS NOT NULL GROUP BY agency ORDER BY 2 DESC
    """), ["Agency", TR])
    st.bar_chart(df, x="Agency", y=TR, horizontal=True)
    n, t = df["Agency"], df[TR]
    insights(
        f"**{n[0]}** handles the most complaints: {t[0]:,} ({pct(t[0], t.sum())} of the workload).",
        f"The top 3 agencies carry **{pct(t[:3].sum(), t.sum())}** of all requests across {len(df)} agencies.",
        f"The busiest agency received **{t[0] / t.median():,.1f} times** as many requests as the middle agency ({t.median():,.0f} requests).",
        f"The lightest load belongs to **{n.iloc[-1]}** with only {t.iloc[-1]:,} requests.",
    )


@analysis("Complaints by Borough")
def by_borough():
    df = frame(filtered_query("""
        SELECT borough, COUNT(*) FROM service_requests
        WHERE borough IS NOT NULL AND borough != 'Unknown' GROUP BY borough ORDER BY 2 DESC
    """), ["Borough", TR])
    st.bar_chart(df, x="Borough", y=TR)
    n, t = df["Borough"], df[TR]
    insights(
        f"**{n[0]}** leads with {t[0]:,} complaints ({pct(t[0], t.sum())} of located complaints).",
        f"**{n.iloc[-1]}** reports the fewest ({t.iloc[-1]:,}), a **{t[0] / t.iloc[-1]:.1f}x** gap from the top borough.",
        f"The top two boroughs ({n[0]} and {n[1]}) together account for **{pct(t[:2].sum(), t.sum())}** of complaints.",
        "A higher number of complaints does not automatically mean a borough has worse service. Population size should also be considered.",
    )


@analysis("Monthly Complaint Trend")
def monthly_trend():
    df = frame(filtered_query("""
        SELECT DATE_FORMAT(created_date, '%Y-%m'), COUNT(*) FROM service_requests
        WHERE created_date IS NOT NULL GROUP BY 1 ORDER BY 1
    """), ["Month", TR])
    st.line_chart(df, x="Month", y=TR)
    m, t = df["Month"], df[TR]
    hi, lo = t.idxmax(), t.idxmin()
    insights(
        f"Peak month is **{m[hi]}** with {t[hi]:,} complaints; the quietest is **{m[lo]}** with {t[lo]:,} ({t[hi] / t[lo]:.1f}x difference).",
        f"The average month sees **{t.mean():,.0f}** complaints, and {(t > t.mean()).sum()} of {len(t)} months are above that.",
        f"Requests in the latest month ({m.iloc[-1]}) changed by **{t.iloc[-1] / t.iloc[-2] - 1:+.1%}** compared with {m.iloc[-2]}. This month may be incomplete.",
        f"From the first to the last month, volume changed by **{t.iloc[-1] / t.iloc[0] - 1:+.1%}**.",
    )



@analysis("Complaints by Weekday and Hour")
def weekday_hour():

    import matplotlib.pyplot as plt

    df = frame(filtered_query("""
        SELECT
            created_weekday,
            created_hour,
            COUNT(*)
        FROM service_requests
        WHERE created_weekday IS NOT NULL
          AND created_hour IS NOT NULL
        GROUP BY created_weekday, created_hour
    """), ["Weekday", "Hour", TR])

    if df.empty:
        st.warning("No weekday and hour data found.")
        return

    df["Hour"] = pd.to_numeric(df["Hour"], errors="coerce")
    df = df.dropna(subset=["Hour", "Weekday"])
    df["Hour"] = df["Hour"].astype(int)

    # Arrange days and hours in correct order
    heatmap_data = df.pivot_table(
        index="Weekday",
        columns="Hour",
        values=TR,
        aggfunc="sum",
        fill_value=0
    )

    heatmap_data = heatmap_data.reindex(
        index=DAYS,
        columns=range(24),
        fill_value=0
    )

    # Create heatmap
    fig, ax = plt.subplots(figsize=(15, 5))

    image = ax.imshow(
        heatmap_data,
        aspect="auto",
        cmap="YlOrRd"
    )

    ax.set_title("Complaints by Weekday and Hour")
    ax.set_xlabel("Hour of the Day")
    ax.set_ylabel("Day of the Week")

    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h}:00" for h in range(24)])

    ax.set_yticks(range(7))
    ax.set_yticklabels(DAYS)

    fig.colorbar(image, ax=ax, label="Number of Complaints")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # Calculate insights
    by_day = heatmap_data.sum(axis=1)
    by_hour = heatmap_data.sum(axis=0)

    busiest_day = by_day.idxmax()
    busiest_hour = by_hour.idxmax()

    busiest_slot = heatmap_data.stack().idxmax()

    weekday_avg = by_day.reindex(DAYS[:5]).sum() / 5
    weekend_avg = by_day.reindex(DAYS[5:]).sum() / 2

    insights(
        f"{busiest_slot[0]} at {busiest_slot[1]}:00 is the busiest time slot.",
        f"{busiest_day} has the highest complaint volume.",
        f"Weekdays average {weekday_avg:,.0f} complaints per day, compared with {weekend_avg:,.0f} on weekends."
    )



@analysis("Request Status Distribution")
def status_distribution():
    df = frame(filtered_query("""
        SELECT status, COUNT(*) FROM service_requests
        WHERE status IS NOT NULL GROUP BY status ORDER BY 2 DESC
    """), ["Status", TR])
    st.bar_chart(df, x="Status", y=TR)
    s, t = df["Status"], df[TR]
    insights(
        f"**{s[0]}** is the dominant status with {t[0]:,} requests ({pct(t[0], t.sum())}).",
        f"{len(df)} distinct statuses are recorded; the rarest, **{s.iloc[-1]}**, has just {t.iloc[-1]:,} requests.",
        f"The overall closure rate is **{pct(closed, total)}**, while **{open_:,}** requests ({pct(open_, total)}) remain unresolved.",
        f"{over_72:,} requests ({pct(over_72, total)}) took more than 72 hours, so 'closed' does not always mean 'closed quickly'.",
    )


@analysis("Resolution Time Statistics")
def resolution_stats():
    n, mean, mn, mx, sd = filtered_query(f"""
        SELECT COUNT(resolution_hours), AVG(resolution_hours), MIN(resolution_hours),
               MAX(resolution_hours), STDDEV_SAMP(resolution_hours)
        FROM service_requests WHERE {VALID}
    """)[0]
    mean, mn, mx, sd = map(float, (mean, mn, mx, sd))
    med = median_resolution
    stats = [
        ("Valid Records", f"{n:,}"),
        ("Mean (Hrs)", f"{mean:,.2f}"),
        ("Median (Hrs)", f"{med:,.2f}"),
        ("Minimum (Hrs)", f"{mn:,.2f}"),
        ("Maximum (Hrs)", f"{mx:,.2f}"),
        ("Std Dev", f"{sd:,.2f}"),
    ]
    for col, (label, value) in zip(st.columns(6), stats):
        col.metric(label, value)
    insights(
        f"The mean ({mean:,.1f} hrs) is **{mean / med:.1f}x** the median ({med:,.1f} hrs), so a few very slow cases pull the average up. Use the median as the 'typical' time.",
        f"Half of all complaints are resolved within **{med:,.1f} hours** (about {med / 24:,.1f} days).",
        f"Resolution times vary a lot. Some complaints are closed quickly, while others take much longer.",
        f"The slowest case took **{mx / 24:,.0f} days** to close. **{pct(over_72, n)}** of valid requests took more than 72 hours.",
    )


def median_by(col, label):
    df = frame(filtered_query(median_sql(col)), [label, "Median Hours", "Valid Requests"])
    st.caption("Showing the 15 slowest")
    st.bar_chart(df.head(15), x=label, y="Median Hours", horizontal=True)
    slow, fast = df.iloc[0], df.iloc[-1]
    insights(
        f"**{slow[label]}** is the slowest, with a median of {slow['Median Hours']:,.1f} hrs ({slow['Median Hours'] / 24:,.1f} days).",
        f"**{fast[label]}** is the fastest at {fast['Median Hours']:,.1f} hrs, a **{slow['Median Hours'] / max(fast['Median Hours'], 0.01):,.0f}x** spread.",
        f"{(df['Median Hours'] > 72).sum()} of {len(df)} groups have a median above 72 hours.",
        f"{(df['Valid Requests'] < 30).sum()} groups have fewer than 30 valid records, so treat their medians with caution.",
    )


analysis("Median Resolution by Complaint Category")(lambda: median_by("complaint_type", "Complaint Category"))
analysis("Median Resolution by Agency")(lambda: median_by("agency", "Agency"))


@analysis("Resolution Time Outlier Analysis")
def outliers():
    q1, q3 = map(float, filtered_query(f"""
        WITH r AS (
            SELECT resolution_hours AS h,
                   ROW_NUMBER() OVER (ORDER BY resolution_hours) AS rn,
                   COUNT(*) OVER () AS n
            FROM service_requests WHERE {VALID}
        )
        SELECT MAX(CASE WHEN rn = FLOOR((n + 3) / 4) THEN h END),
               MAX(CASE WHEN rn = FLOOR((3 * n + 3) / 4) THEN h END)
        FROM r
    """)[0])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    valid, n_out = filtered_query(
        f"SELECT COUNT(*), SUM(resolution_hours > %s) FROM service_requests WHERE {VALID}",
        (upper,),
    )[0]
    n_out = int(n_out or 0)

    for col, (label, value) in zip(st.columns(5), [
        ("Q1 (Hrs)", q1),
        ("Q3 (Hrs)", q3),
        ("IQR (Hrs)", iqr),
        ("Upper Limit (Hrs)", upper),
        ("Outliers", n_out),
    ]):
        col.metric(label, f"{value:,.2f}" if isinstance(value, float) else f"{value:,}")

    st.bar_chart(pd.DataFrame(
        {"Hours": [q1, median_resolution, q3, upper]},
        index=["1. Q1", "2. Median", "3. Q3", "4. Upper limit"],
    ))
    insights(
        f"**{n_out:,} requests ({pct(n_out, valid)})** exceed the upper limit of {upper:,.1f} hrs ({upper / 24:,.1f} days).",
        f"The middle 50% of complaints are resolved between **{q1:,.1f} and {q3:,.1f} hours** (IQR = {iqr:,.1f}).",
        f"The outlier cutoff is **{upper / median_resolution:,.1f}x** the median, so anything beyond it is an unusually slow case."
        + (" The lower limit is below zero, so only slow outliers exist." if lower < 0 else ""),
        "These unusually slow cases are kept in the dataset because they may represent real delays that need investigation.",
    )


@analysis("Resolution Time Distribution and Skewness")
def distribution():
    n, mean, sd = filtered_query(f"""
        SELECT COUNT(*), AVG(resolution_hours), STDDEV_POP(resolution_hours)
        FROM service_requests WHERE {VALID}
    """)[0]
    mean, sd = float(mean), float(sd)
    skew = filtered_query(f"""
        SELECT AVG(POWER(resolution_hours - %s, 3)) / POWER(%s, 3)
        FROM service_requests WHERE {VALID}
    """, (mean, sd))[0][0]
    skew = float(skew) if skew is not None else None

    for col, (label, value) in zip(st.columns(3), [
        ("Valid Records", f"{n:,}"),
        ("Mean Resolution", f"{mean:,.2f} hrs"),
        ("Skewness", f"{skew:,.2f}" if skew is not None else "N/A"),
    ]):
        col.metric(label, value)

    df = frame(filtered_query(f"""
        SELECT CASE WHEN resolution_hours < 1 THEN '1. Under 1h'
                    WHEN resolution_hours < 6 THEN '2. 1-6h'
                    WHEN resolution_hours < 24 THEN '3. 6-24h'
                    WHEN resolution_hours < 72 THEN '4. 1-3 days'
                    WHEN resolution_hours < 168 THEN '5. 3-7 days'
                    ELSE '6. Over 7 days' END AS bucket,
               COUNT(*)
        FROM service_requests WHERE {VALID} GROUP BY bucket ORDER BY bucket
    """), ["Resolution Window", TR])
    st.bar_chart(df, x="Resolution Window", y=TR)

    first = df["Resolution Window"].str[0]
    within_24 = df.loc[first.isin(["1", "2", "3"]), TR].sum()
    over_7d = df.loc[first == "6", TR].sum()
    if skew is None:
        shape = "could not be calculated"
    elif abs(skew) < 0.5:
        shape = "roughly symmetric"
    else:
        shape = f"{'strongly' if abs(skew) > 1 else 'moderately'} {'right' if skew > 0 else 'left'}-skewed"
    insights(
        f"Skewness is **{skew:.2f}**, so the distribution is **{shape}**: most complaints close quickly while a minority take far longer."
        if skew is not None else "Skewness could not be calculated (not enough variation).",
        f"The mean ({mean:,.1f} hrs) sits {mean / median_resolution:,.1f}x above the median ({median_resolution:,.1f} hrs), another sign of a long right tail.",
        f"**{pct(within_24, n)}** of complaints are resolved within 24 hours.",
        f"Only **{pct(over_7d, n)}** take more than 7 days, but these cases drive the high average and deserve a root-cause review.",
    )


@analysis("Geographic Complaint Concentration")
def geo_concentration():
    df = frame(filtered_query("""
        SELECT borough, COUNT(*) FROM service_requests
        WHERE borough IS NOT NULL AND borough != 'Unknown' GROUP BY borough ORDER BY 2 DESC
    """), ["Borough", "Total Complaints"])
    df["Share (%)"] = df["Total Complaints"] / df["Total Complaints"].sum() * 100
    st.bar_chart(df, x="Borough", y="Share (%)")
    n, s = df["Borough"], df["Share (%)"]
    hhi, k = ((s / 100) ** 2).sum(), len(df)
    insights(
        f"**{n[0]}** alone generates **{s[0]:.1f}%** of all located complaints.",
        f"The top two boroughs ({n[0]}, {n[1]}) together account for **{s[:2].sum():.1f}%**.",
        f"{'A large share of complaints comes from a few boroughs.' if hhi * k > 1.3 else 'Complaints are spread fairly evenly across the boroughs.'}",
        f"The share of complaints in {n[0]} is **{s[0] / s.iloc[-1]:.1f} times** the share in {n.iloc[-1]}.",
    )


@analysis("Agency Closure Rate Comparison")
def closure_rates():
    df = frame(filtered_query("""
        SELECT agency, COUNT(*), SUM(is_closed), ROUND(SUM(is_closed) * 100.0 / COUNT(*), 2)
        FROM service_requests WHERE agency IS NOT NULL GROUP BY agency ORDER BY 4 DESC
    """), ["Agency", TR, "Closed Requests", "Closure Rate (%)"])
    df["Open Requests"] = df[TR] - df["Closed Requests"]
    st.bar_chart(df, x="Agency", y="Closure Rate (%)", horizontal=True)

    rate = df["Closure Rate (%)"]
    overall = df["Closed Requests"].sum() / df[TR].sum() * 100
    backlog = df.loc[df["Open Requests"].idxmax()]
    insights(
        f"**{df['Agency'][0]}** has the best closure rate ({rate.iloc[0]:.1f}%); **{df['Agency'].iloc[-1]}** has the lowest ({rate.iloc[-1]:.1f}%), a gap of {rate.iloc[0] - rate.iloc[-1]:.1f} points.",
        f"The overall closure rate is **{overall:.1f}%**, and {(rate < overall).sum()} of {len(df)} agencies fall below it.",
        f"**{backlog['Agency']}** holds the largest backlog with {int(backlog['Open Requests']):,} open requests.",
        f"{(rate >= 100).sum()} agencies have closed every request they received.",
    )


@analysis("High-Volume Complaints with Long Resolution")
def high_volume_slow():
    df = frame(filtered_query(f"""
        SELECT complaint_type, COUNT(*), ROUND(AVG(resolution_hours), 2)
        FROM service_requests
        WHERE complaint_type IS NOT NULL AND {VALID}
        GROUP BY complaint_type HAVING COUNT(*) >= 100
        ORDER BY 3 DESC LIMIT 10
    """), ["Complaint Category", TR, "Average Resolution (Hours)"])
    st.bar_chart(df, x="Complaint Category", y="Average Resolution (Hours)", horizontal=True)

    n, v, h = df["Complaint Category"], df[TR], df["Average Resolution (Hours)"]
    burden = (v * h).idxmax()
    insights(
        f"**{n[0]}** is the slowest high-volume category, averaging {h[0]:,.1f} hrs ({h[0] / 24:,.1f} days) across {v[0]:,} requests.",
        f"This category's average closure time is **{h[0] / median_resolution:,.1f} times** the overall middle closure time. A few very slow cases can increase an average.",
        f"{(h > 72).sum()} of these 10 categories average more than 72 hours.",
        f"**{n[burden]}** has the largest combined delay because it has many requests and a high average closure time.",
    )


# --------------------------------------------------
# Sidebar menu and page
# --------------------------------------------------
selected = st.sidebar.selectbox("Select an Analysis", list(ANALYSES))
st.header(selected)

try:
    ANALYSES[selected]()
except mysql.connector.Error as error:
    st.error(f"Database error: {error}")
