## sources/storage-engines/wiredtiger/test/suite/test_cursor_random.py

### Purpose
`test_cursor_random.py` validates `next_random` cursor behavior. It covers unsupported operations, empty and single-record trees, randomness over insert-list and disk-page records, deleted ranges, unsupported column stores, and invisible transactional updates.

### Important APIs, Types, and Functions
The file defines three test classes: `test_cursor_random`, `test_cursor_random_column`, and `test_cursor_random_invisible`. It uses `SimpleDataSet`, `ComplexDataSet`, `simple_key`, `simple_value`, `make_scenarios`, `session.open_cursor(..., "next_random=true...")`, optional `next_random_sample_size`, `cursor.next`, `cursor.reconfigure`, `cursor.reset`, unsupported-operation assertions, `truncate`, and `reopen_conn`.

### Control Flow and State
The main class runs file/table scenarios with sampled and unsampled random cursor configs. It verifies unsupported methods (`compare`, `insert`, `prev`, `remove`, `search`, `search_near`, `update`) fail while `next`, `reconfigure`, and `reset` are allowed. Empty trees repeatedly return not-found; single-record trees repeatedly return the same key. Multi-record helpers populate 2,000 or 10,000 records and assert 99 random reads yield more than 80 unique keys, both in insert-list state and after optional reopen to disk pages. Deleted-partial tests truncate most records but expect random next to find remaining ones; deleted-all expects not-found. Column-store class asserts opening next-random on `key_format=r` fails. Invisible tests use uncommitted updates in one session and random cursors in another to ensure only committed visible records can be returned.

### Persistence and Integration
The suite covers in-memory insert lists, reopened disk pages, truncation tombstones, and transaction isolation. macOS-specific eviction warnings are ignored after deliberate connection close.

### Risks and Test Signals
Risks include random cursor methods exposing unsupported operations, sampling bias/regression, returning deleted or uncommitted records, and allowing unsupported column-store random cursors. Passing confirms random selection respects visibility and API limits.
