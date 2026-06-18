## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound19.py

### Purpose
`test_cursor_bound19.py` tests bounds on index cursors, including duplicate index values. It verifies traversal counts, search-near positioning, exact search, reset, clear, and exclusive lower-bound behavior for secondary indexes.

### Important APIs, Types, and Functions
The class derives from `bound_base`, sets `use_index=True`, and runs table/column-group scenarios with many key and value formats. It creates an index URI `index:<file_name>:i0` over all value columns, opens an index cursor, and uses `set_bounds`, `cursor_traversal_bound`, `search_near`, `search`, and `reset`.

### Control Flow and State
`create_session_and_cursor` first populates the primary table with duplicate values for index testing, then the test creates the index. It sets lower 30 and upper 40; because duplicate values are generated up to the range, traversal expects 22 entries. Search-near below, inside, and above the range should return 30, 35, and 40 respectively; exact search outside the range should be not found. After `reset`, full traversal expects 60 index entries. After `action=clear`, full traversal is rechecked. The exclusive lower-bound case excludes duplicates at 30, yielding 20 entries and moving a below-range search-near to 31.

### Persistence and Integration
The test integrates cursor bounds with secondary index key/value encoding and duplicate index entries. Column-group table scenarios exercise index creation over table layouts with column groups.

### Risks and Test Signals
Risks include applying bounds to primary keys instead of index keys, duplicate handling off-by-one errors, reset/clear not restoring full index traversal, and exclusive lower bounds failing to skip duplicates. Passing confirms index cursor bounds are value-key-aware.
