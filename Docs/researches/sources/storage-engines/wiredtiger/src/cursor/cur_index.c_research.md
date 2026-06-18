# sources/storage-engines/wiredtiger/src/cursor/cur_index.c

## Purpose
`cur_index.c` implements read-only secondary-index cursors for WiredTiger tables. An index cursor scans an index btree, exposes the index key to the user, and reconstructs requested table values by positioning the necessary column-group cursors on the primary key carried inside each index entry.

## Important APIs, Types, and Functions
The exported entry point is `__wt_curindex_open`. It parses `index:<table>:<index>` URIs, opens the table and index metadata, initializes a `WT_CURSOR_INDEX`, opens the child cursor on `idx->source`, and opens only the column-group cursors needed by the index cursor projection. `__curindex_get_value` delegates to the inline `__wt_curindex_get_valuev`, while `__curindex_set_valuev` always returns `ENOTSUP` because index cursors are read-only.

`__curindex_move` is the core positioning helper. After the child index cursor moves, it exposes the child key through the public cursor, projects the primary-key columns out of the index key with `__wt_schema_project_slice`, copies that key to all required column-group cursors, and searches the column groups whose values are needed. `__curindex_search` and `__curindex_search_near` implement prefix-aware lookup because user-specified index keys usually omit the appended primary key.

## Control Flow
Opening first resolves table/index metadata, handles optional projection syntax in the URI, computes cursor value format and projection plan if projection columns were supplied, initializes the public cursor, opens the child index btree cursor, and opens required column groups with dump disabled. JSON dump column metadata is initialized when needed.

Iteration calls the child cursor's `next` or `prev`, then `__curindex_move`. Search sets the raw child key to the user key, calls child `search_near`, steps forward when it lands below the prefix, validates the found key has the requested prefix, repacks for custom collators when needed, and then moves column-group cursors. Search-near follows similar prefix logic but returns an exact sign that matches public cursor expectations. Reset resets both child and column-group cursors and clears child bounds on user-visible reset.

## State and Persistence Behavior
Index cursors are read-only. They persist no data directly and reject insert, update, remove, modify, reserve, cache, reopen, and largest-key operations. Their state is a coordinated set of cursor positions: the index child cursor determines the public key, and column-group cursors are positioned to provide table values. Projection plans and formats may be borrowed from metadata or allocated for a projected cursor and are freed on close.

## Dependencies and Integration Points
The implementation depends on schema metadata (`WT_TABLE`, `WT_INDEX`, column groups), structure packing/reformatting/planning helpers, collators, child file cursors, JSON column initialization, and bounded cursor helpers. `session_api.c` dispatches `index:` URIs here. Table cursor code coordinates with index cursors during table operations, and docs explicitly present table/index cursors as schema-layer cursor types.

## Risks and Edge Cases
Prefix matching is subtle because internal index keys append primary-key columns for uniqueness while users search only the declared index key. Custom collators require complete visible fields, so the code repacks found keys before comparison. Bound handling has special byte-increment logic: exclusive lower bounds and inclusive upper bounds must be shifted because the hidden primary key suffix is not part of the user's bound. Fixed-length all-`UINT8_MAX` lower bounds cannot be incremented and return `EINVAL`; all-maximum upper bounds clear the upper bound. Column-store indexes based only on a recno primary key are explicitly rejected.

## Test Signals
Index cursor coverage includes `test_index01.py`, custom-collator duplicate index tests, bounded cursor prefix-index C++ coverage, and `test_cursor_bound19.py`/`test_cursor_bound20.py` for basic and edge-case index bounds. Additional useful signals would include projected value retrieval across multiple column groups, prefix searches with custom collators, exact-sign behavior for search-near around duplicate index prefixes, and close cleanup after partial open failure.
