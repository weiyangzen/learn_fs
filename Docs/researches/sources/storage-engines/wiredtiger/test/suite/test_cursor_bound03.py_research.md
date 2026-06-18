## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound03.py

### Purpose
`test_cursor_bound03.py` verifies `next()` and `prev()` traversal with cursor bounds. It exercises lower-only, upper-only, both-bound, out-of-data-range, empty-range, changed-bound, and cleared-bound cases across object and schema scenarios.

### Important APIs, Types, and Functions
The test inherits from `bound_base` and uses scenario dimensions for object type, key format, value format, evict/no-evict, inclusive combinations, and direction. It depends heavily on `create_session_and_cursor`, `set_bounds`, `cursor_traversal_bound`, `cursor.bound("action=clear")`, and `cursor.reset`.

### Control Flow and State
The helper creates and populates the table with keys 20 through 79, optionally evicting pages. The test sets an upper bound at 50 and traverses, clears it, then sets a lower bound at 45 and traverses. It repeats with both bounds, with bounds beyond the stored data range, and with a range containing no data. It verifies clearing bounds restores full traversal. Later cases mutate upper and lower bounds from one value to another, both within range and across out-of-range values, and validate traversal count/key constraints after each change.

### Persistence and Integration
State is persistent table data inserted by `bound_base`; eviction scenarios force both in-memory and on-disk cursor paths. The same assertions cover row, column, byte-array, and composite key encodings.

### Risks and Test Signals
The suite catches off-by-one inclusivity errors, early exit mistakes at bounds, failure to reconfigure active bounds, and differences between forward and reverse traversal. Passing gives strong signal that bounded cursor traversal respects configured ranges after repeated clear/change cycles.
