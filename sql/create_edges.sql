/*
* Creates the edges table, accounting for redirects
* Represents all the connections between pages in Wikipedia
*/
CREATE TABLE edges
( 
  from_page_id INT NOT NULL, 
  to_page_id INT NOT NULL, 
  PRIMARY KEY (from_page_id, to_page_id), INDEX (to_page_id) 
);

INSERT IGNORE INTO edges
SELECT 
  pl.pl_from,
  COALESCE(redirect_target.page_id, p2.page_id)
FROM pagelinks_ns0 pl
JOIN linktarget lt
  ON pl.pl_target_id = lt.lt_id
JOIN page p2
  ON p2.page_title = lt.lt_title 
  AND p2.page_namespace = 0
LEFT JOIN redirect rd
  ON rd.rd_from = p2.page_id
LEFT JOIN page redirect_target
  ON redirect_target.page_title = rd.rd_title
  AND redirect_target.page_namespace = rd.rd_namespace
WHERE (p2.page_is_redirect = 0 OR redirect_target.page_id IS NOT NULL)
  AND pl.pl_from >= $start
  AND pl.pl_from < $end;
