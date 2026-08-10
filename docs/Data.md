# Data - Wiki-Pathfinder

## Steps
  - [Data Acquisition](#Data-Acquisition)
  - [Cleaning](#Cleaning)
  - [Building .bin Files and Compressed Sparse Row (CSR)](#Building-.bin-files-and-Compressed-Sparse-Row-(CSR))
  - [Title Search and Autocomplete](#Title-Search-and-Autocomplete)
  - [Loading the Data](#Loading-the-Data)


# Data Acquisition

The data used in this project was acquired from [Wikimedia's](#https://dumps.wikimedia.org/backup-index.html) enwiki dump, which contains zipped MYSQL dumps of the English wikipedia dumped monthly. The project primarily uses the page, pagelinks, and linktarget table dumps.

# Cleaning

The page, pagelinks, and linktarget tables in total take up around 200 GB of memory once imported. The databases are cleaned by removing all articles and links not of namespace 0 (main page articles). More infomation on these tables can be found [here](#https://www.mediawiki.org/wiki/Manual:Database_layout). The structure of the post-cleaned tables are depicted below:

  1. 'page' - Contains page information and names
     1. 'page_id'- Primary Key, unique page ID
     2. 'page_title" - page title in binary
     3. 'page_is_redirect' - 1 for a redirect page, 0 otherwise
  2. 'pagelinks' - contains information regarding article links
     1. 'pl_from' - page ID of page containing the link
     2. 'pl_target_id' - page the link points to as a foreign key to linktarget
  3. 'linktarget' - table containing information to connect links to their destination articles
     1. lt_id - Primary key and foreign key of pagelinks
     2. lt_title - page title in binary

pagelinks and linktarget are then consolidated into a single edges table containing every unique link as a composite key of the page_id they reside in and the page_id they point to. Redirects are treated as unique links, and the page_is_redirect column is removed from the page table. The edges and page tables can be found as MYSQL dumps [here](#https://drive.google.com/drive/folders/1zovQapluH6LGg_0V8Q7cpqaH-F0wSjCb?usp=drive_link). The structure of the edge table is depicted below:
1. 'edges' - Contains every link as a pair of page IDs
   1. 'from_page_id': page ID the link resides in
   2. 'to_page_id': page ID the link points to

# Building .bin Files and Compressed Sparse Row (CSR)

Wiki-Pathfinder utilizes .bin files to ultimately store the data. As page IDs are non-sequential, they are first mapped to sequential node IDs before being converted to .bin files. The .bin files can be found [here](#https://drive.google.com/drive/folders/1zovQapluH6LGg_0V8Q7cpqaH-F0wSjCb?usp=drive_link), and are listed below:
### CSR Graph Representation
  1. 'forward_neighbors' - A 1D array of all forward edge destinations
  2. 'reverse_neighbors' - A 1D array of all reverse edge destinations
  3. 'forward_offsets' - A 1D array of forward offsets, the neighbors of node 1 would be found by searching neighbors from index offsets[1] to offsets[2]
  4. 'forward_offsets' - A 1D array of reverse offsets, the neighbors of node 1 would be found by searching neighbors from index offsets[1] to offsets[2]

### Title Search and Autocomplete
  1. 'title_to_node' - a dictionary that maps each node to its title
  2. 'titles' - a 1D array of titles whose indexes correspond to nodes
  3. 'sorted_title_strings' - a 1D arrays of alphabetically sorted titles in lowercase
  4. 'autocomplete' - a 1D array of (node, incoming links) pairs sorted alphabetically by title
  5. 'is_redirect_array' - a 1D array whose indexes correspond to nodes '1: redirect, 0: non-redirect'

# Loading the Data

The .bin files are loaded into RAM at server start. Memory mapping is used for .bin files comprising the CSR Graph Representation.
