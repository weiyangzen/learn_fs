## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound11.py

### Purpose
`test_cursor_bound11.py` tests prefix search scenarios migrated to bounded cursor logic. It focuses on performance/skip behavior and row-search guarantees when prefix ranges contain invisible, deleted, or prepared updates.

### Important APIs, Types, and Functions
The class derives directly from `wttest.WiredTigerTestCase`, enables statistics, and uses `wtbound.set_prefix_bound`. Helpers include `get_stat` for statistics cursors and `unique_insert`, which models unique-index insertion by inserting a prefix key, removing it, searching near it, then inserting a full `(prefix,id)`-style key.

### Control Flow and State
`test_base_scenario` inserts all keys `aaa` through `zzz`, starts an older reader, evicts pages, and compares unbounded `search_near('aa')` skip counts with prefix-bounded searches for `aa` and `bb`. `test_unique_index_case` simulates unique-index insertion patterns for prefixes `aa` through `zz`, skipping `cc`, and verifies prefix bounds limit search work and early-exit stats. `test_row_search` verifies assumptions around invisible inserted keys and removed adjacent keys. `test_prepared` combines an older reader, a visible committed `cc`, prepared updates for most prefixes, eviction, prefix-bounded search-near, and `ignore_prepare=true`.

### Persistence and Integration
The tests rely on committed data, older read transactions, prepared transactions, eviction, and connection statistics. They integrate prefix-bound construction with search-near optimization counters.

### Risks and Test Signals
Risks include prefix-bounded search-near traversing entire keyspaces, cursor-cache flags surviving cursor reopen, row-search skip-count assumptions breaking, and prepared invisible data defeating early exit. Passing confirms prefix bounds can optimize search without losing correctness.
