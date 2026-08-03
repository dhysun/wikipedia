/*
* pagelinks was imported from the Wikipedia dump.
* After importing, we filtered for rows with namespace = 0
*/

CREATE TABLE pagelinks_ns0 (
  pl_from INT UNSIGNED NOT NULL,
  pl_target_id BIGINT UNSIGNED NOT NULL
);

INSERT INTO pagelinks_ns0 (pl_from, pl_target_id)
SELECT pl_from, pl_target_id
FROM pagelinks
WHERE pl_from_namespace = 0;