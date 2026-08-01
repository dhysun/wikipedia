/**
*Filters for namespace 0 (main articles) for the page table. Done by creating a new table and dropping the original,
*though it can also be done via delete queries 
*/

CREATE TABLE page_main AS
SELECT *
FROM page
WHERE page_namespace = 0;
