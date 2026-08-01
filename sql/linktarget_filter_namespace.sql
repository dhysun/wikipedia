/**
*Filters for namespace 0 (main articles) for the linktarget table. Done by creating a new table and dropping the original,
*though it can also be done via delete queries 
*/

CREATE TABLE linktarget_filtered AS
SELECT *
FROM linktarget
WHERE lt_namespace = 0;
