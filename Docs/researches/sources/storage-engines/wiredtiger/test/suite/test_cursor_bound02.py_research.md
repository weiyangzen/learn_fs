## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound02.py

### Purpose
`test_cursor_bound02.py` validates bound setting, ordering, inclusivity, key persistence, reset, and clear semantics across many key/value schemas and object types. It is a broad API-level correctness suite for lower/upper bound configuration.

### Important APIs, Types, and Functions
The class derives from `bound_base` and expands scenarios over `file:`, `table:`, column-group tables, key formats `S`, `r`, `i`, `u`, `SSS`, `iS`, and `iSru`, value formats `S` and `SS`, plus inclusive/exclusive configurations. It relies on `set_bounds`, `gen_create_param`, `gen_key`, `gen_val`, `cursor.bound`, `cursor.reset`, `cursor.insert`, and `assertRaisesWithMessage`.

### Control Flow and State
`test_bound_api` creates an object, optionally creates column groups, and opens a cursor. It sets a lower bound then an upper bound, checks that inverted upper/lower assignments fail, then verifies valid bound changes in both directions. It checks that a missing key causes bound setting to fail and that the cursor key remains usable for `insert` after setting lower or upper bounds. Equal lower/upper bounds are allowed only when both sides are inclusive; attempts to mix exclusivity at an equal key fail. `test_bound_api_reset` verifies `cursor.reset()` clears bounds enough to allow previously invalid bound changes. `test_bound_api_clear` checks repeated `action=clear` and clearing one or both bounds before setting new ranges.

### Persistence and Integration
Inserted records at keys 30 and 90 prove bound calls do not consume or clear the cursor key/value. Column groups exercise bound propagation to underlying column group cursors.

### Risks and Test Signals
The test guards against stale bounds surviving reset/clear, invalid range acceptance, equal-bound inclusivity bugs, and composite-format packing mistakes. Passing confirms the bound API can be reused safely across schema shapes.
