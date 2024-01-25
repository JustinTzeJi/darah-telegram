SELECT donor_id, visit_date, sum(donation_num)OVER(PARTITION BY donor_id
    ORDER BY visit_date ASC) as donation_num FROM
(SELECT donor_id, DATE(visit_date) visit_date, count(*) AS donation_num
FROM `articulate-case-410317.data_darah.blood-donation-retention`
GROUP BY 1,2)
ORDER BY 1,2