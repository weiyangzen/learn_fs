## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound06.py

### Purpose
`test_cursor_bound06.py` validates `cursor.search()` with bounds. It checks unbounded searches, searches outside lower or upper bounds, searches inside both bounds, and searches exactly on inclusive/exclusive boundary keys.

### Important APIs, Types, and Functions
The class inherits from `bound_base`, expands scenarios over file/table/column-group objects, many key formats, value formats, inclusive/exclusive settings, and eviction. It uses `create_session_and_cursor`, `set_bounds`, `cursor.set_key`, `cursor.search`, `cursor.reset`, `wiredtiger.WT_NOTFOUND`, and `cursor.close`.

### Control Flow and State
After population, the test first searches for a non-existent key without bounds and expects `WT_NOTFOUND`, then searches for existing key 50 and expects success. It sets a lower bound at 30 and searches key 20, then an upper bound at 40 and searches key 60; both must return not found. With lower 20 and upper 40, searching key 35 succeeds. It checks keys adjacent to bounds and exact bound equality. For exact bound searches, success depends on the `inclusive` scenario flag; exclusive boundaries must return `WT_NOTFOUND`.

### Persistence and Integration
Data is the standard `bound_base` key range, optionally evicted. The test integrates boundary comparison logic with search rather than traversal, covering row, record-number, byte-array, and composite-key encodings.

### Risks and Test Signals
The test catches search paths that ignore bounds, mishandle equality at exclusive endpoints, or compare packed composite/byte keys incorrectly. Passing confirms `search()` applies bound filters before reporting an exact match.
