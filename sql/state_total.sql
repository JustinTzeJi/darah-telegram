WITH
  A AS (
  SELECT
    DATE(date) AS date,
    EXTRACT(YEAR
    FROM
      DATE(date)) year,
    state,
    daily,
    SUM(daily) OVER (PARTITION BY state, EXTRACT(YEAR FROM DATE(date))
    ORDER BY
      DATE(date) ASC) AS cumulative_daily_donations
  FROM
    `articulate-case-410317.data_darah.donations_state`
  WHERE
    state != "Malaysia")

SELECT
  c.date,c.state,
  B.* except(date,state),
  C.cumulative_daily_donations cumulative_daily_donations_prev_year
FROM (
  SELECT
    * EXCEPT( year)
  FROM
    A
  WHERE
    date >= DATE_TRUNC(CURRENT_DATE("Asia/Kuching"), YEAR) ) B
FULL JOIN (
  SELECT
    * EXCEPT(date,
      year),
    DATE_ADD(date, INTERVAL 1 YEAR) AS date
  FROM
    A
  WHERE
    date between date_sub( DATE_TRUNC(CURRENT_DATE("Asia/Kuching"), YEAR) , interval 1 YEAR) AND date_sub(date_add(CURRENT_DATE("Asia/Kuching"), interval 1 WEEK), interval 1 YEAR) ) C
	
ON
  B.date = C.date
  AND B.state = C.state
ORDER BY 2,1