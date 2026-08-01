/*
*creates the edges table. Represents all the connections between pages in Wikipedia
*/
CREATE TABLE edges
( 
  from_page_id INT NOT NULL, 
  to_page_id INT NOT NULL, 
  PRIMARY KEY (from_page_id, to_page_id), INDEX (to_page_id) 
);
