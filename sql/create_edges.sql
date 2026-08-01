/*
*creates the edges table. Represents all the connections between pages in Wikipedia
*/
CREATE TABLE edges
( 
  from_page_id INT NOT NULL, 
  to_page_id INT NOT NULL, 
  PRIMARY KEY (from_page_id, to_page_id), INDEX (to_page_id) 
);

INSERT INTO edges 
SELECT 
  pagelinks.pl_from, 
  page.page_id 
FROM pagelinks 
JOIN linktarget
  ON pagelinks.pl_target_id = linktarget.lt_id 
JOIN page 
  ON page.page_title = linktarget.lt_title; 
