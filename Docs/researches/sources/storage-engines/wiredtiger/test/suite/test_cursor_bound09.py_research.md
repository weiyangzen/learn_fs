## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound09.py

### Purpose
`test_cursor_bound09.py` validates bounded cursor behavior in the presence of prepared updates. It checks `search`, `search_near`, `next`, and `prev` with and without `ignore_prepare=true`, including prepared keys at boundaries and out-of-bound search-near inputs.

### Important APIs, Types, and Functions
The class uses `bound_base`, `make_scenarios`, `wiredtiger_strerror`, `WT_PREPARE_CONFLICT`, `WiredTigerError`, and `wiredtiger.WT_NOTFOUND`. It expands over object type, key format, inclusive/eviction settings, and ignore-prepare mode. It uses separate sessions, prepared transactions, `set_bounds`, cursor operations, and explicit rollback of prepared transactions.

### Control Flow and State
The test populates the standard key range, then prepares updates on keys 30-35. A second session opens a bounded cursor over 20-40 and runs search-like operations on key 30. Without `ignore_prepare`, prepare conflicts are accepted; with `ignore_prepare`, operations must return valid results subject to exclusivity. It repeats with a bound exactly on prepared key 30 and validates `prev` behavior. It then rolls back, prepares keys 29-30, and tests `search_near` from key 20 with lower bound 30. Final logic checks non-inclusive bounds where `next()` may hit a prepare conflict and leave the cursor key at the prepared boundary.

### Persistence and Integration
Prepared updates are held open across sessions and then rolled back. This directly exercises WiredTiger conflict handling in bounded traversal and search paths.

### Risks and Test Signals
The suite catches bugs where bounds hide prepare conflicts, return unprepared keys out of order, or corrupt cursor key state after conflicts. Passing confirms bounded operations honor prepare isolation and `ignore_prepare`.
