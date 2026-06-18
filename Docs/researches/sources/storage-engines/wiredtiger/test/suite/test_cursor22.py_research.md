## sources/storage-engines/wiredtiger/test/suite/test_cursor22.py

### Purpose
`test_cursor22.py` is a focused Python suite for `WT_CURSOR.get_raw_key_value()` on a simple row-store table with `key_format=S,value_format=S`. It establishes that raw key/value retrieval returns the same logical data as `get_key()` and `get_value()`, and that callers may ignore either or both tuple elements without side effects.

### Important APIs, Types, and Functions
The test class `test_cursor22` derives from `wttest.WiredTigerTestCase`. It uses `session.create`, `session.open_cursor`, explicit `begin_transaction`/`commit_transaction`, `cursor.set_key`, `cursor.set_value`, `cursor.insert`, `cursor.reset`, `cursor.next`, `cursor.get_key`, `cursor.get_value`, `cursor.get_raw_key_value`, and `cursor.close`. Helper methods `check_get_key_and_value` and `check_get_raw_key_value` centralize expected key/value assertions.

### Control Flow and State
The test creates `table:test_cursor22`, inserts keys `key1` through `key9` with values `value101` through `value109` inside one transaction, then scans the table twice in separate transactions. The first scan validates the standard cursor accessors; the second validates `get_raw_key_value`. A final transaction positions at the first row and exercises tuple unpacking patterns: keeping only the key, discarding the returned tuple entirely, and keeping only the value.

### Persistence and Integration
State is persisted through normal WiredTiger table inserts and transaction commits. The test integrates with the Python SWIG cursor binding and depends on cursor positioning from `next()`. It is intentionally independent of datasets or scenario expansion, making it a narrow regression signal for the raw accessor binding.

### Risks and Test Signals
The main risk covered is divergence between raw and decoded key/value accessors for simple string schemas, especially tuple lifetime or SWIG ownership issues when elements are ignored. Passing signals that positioned cursors return stable raw tuples and that repeated raw accesses do not invalidate cursor state.
