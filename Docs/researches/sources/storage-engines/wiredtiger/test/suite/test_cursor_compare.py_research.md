## sources/storage-engines/wiredtiger/test/suite/test_cursor_compare.py

### Purpose
`test_cursor_compare.py` validates `WT_CURSOR.compare` and `WT_CURSOR.equals` behavior for file, table, and index cursors. It checks key ordering/equality, required key state, object identity restrictions, and platform-specific exception wrapping for null cursor arguments.

### Important APIs, Types, and Functions
The class `test_cursor_comparison` uses `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, `cursor.compare`, `cursor.equals`, `cursor.set_key`, `cursor.search`, index cursor opening via `ds.index_name`, and error assertions. It selects `TypeError` on Darwin and `RuntimeError` elsewhere for SWIG null-pointer behavior.

### Control Flow and State
For each file/table and integer/record-number/string key scenario, the test populates two separate objects. Table scenarios also open multiple index cursors: two on the same index, one on another index, and one on the other table. `test_cursor_comparison` first asserts compare fails when keys are unset, then compares unset-position cursors with only key fields assigned. It checks comparisons against different objects and null. It verifies same-index comparisons and rejects main-table-vs-index, unrelated index, and different-index comparisons. It repeats after positioning cursors with `search`. `test_cursor_equality` mirrors the same structure for boolean equality.

### Persistence and Integration
Dataset helpers create both simple file objects and complex indexed tables. The tests integrate Python bindings with cursor object identity and key comparison rules across primary and secondary cursors.

### Risks and Test Signals
Risks include comparing cursors from different objects, requiring physical positioning when a key is already set, index identity confusion, and inconsistent SWIG exception behavior. Passing confirms compare/equals semantics are stable for public cursor APIs.
