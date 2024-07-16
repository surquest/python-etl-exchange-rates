SELECT MAX(a.date)                  AS date,
       a.currency_base              AS base,
       a.currency_quote             AS currency,
       ARRAY_AGG(a.exchange_rate IGNORE NULLS ORDER BY a.date DESC LIMIT 1)[SAFE_OFFSET(0)] AS exchange_rate,
       ARRAY_AGG(a.created_at IGNORE NULLS ORDER BY a.date DESC LIMIT 1)[SAFE_OFFSET(0)] AS __record_create_date
FROM ${dataset}.fx_history a
WHERE UPPER(a.currency_base) = '${currency}'
GROUP BY a.currency_base, a.currency_quote