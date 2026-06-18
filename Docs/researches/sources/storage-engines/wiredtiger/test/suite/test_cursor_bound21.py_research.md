## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound21.py

### Purpose
`test_cursor_bound21.py` validates prepare-conflict correctness when a bounded cursor positions for `next()` and `prev()`. It covers inclusive and non-inclusive bounds and cases where the prepared key is missing from the committed key set.

### Important APIs, Types, and Functions
The class derives from `bound_base` and runs key formats `S`, `r`, `i`, and `u`. It uses separate sessions/cursors, prepared transactions, `cursor.bound`, `cursor.next`, `cursor.prev`, `wiredtiger_strerror`, `WT_PREPARE_CONFLICT`, `WiredTigerError`, and commit with durable timestamps.

### Control Flow and State
`test_cursor_bound_bug` prepares key 1, sets a lower bound at key 1 in another cursor, and calls `next()` three times, expecting only prepare conflicts. After commit, `next()` must return key 1. It repeats symmetrically with key 2 and an upper bound using `prev()`. `test_not_inclusive_bound` sets a lower exclusive bound matching prepared keys; when a committed key exists beyond the bound, next can skip the bound key, but a later prepared range should still conflict before commit and return key 4 after commit. `test_missing_bound_key_prepare` inserts committed keys 1, 5, and 10, prepares missing key 4, sets lower bound 2, expects repeated prepare conflicts, then after commit expects key 4.

### Persistence and Integration
Prepared state persists across sessions until commit. Byte-array key scenarios normalize expected keys through decoding.

### Risks and Test Signals
The covered risk is a bounded positioning loop returning not-found, a wrong key, or stale cursor state instead of a prepare conflict. Passing confirms conflict detection remains stable across repeated calls and after commit.
