## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound01.py

### Purpose
`test_cursor_bound01.py` performs basic validation of the cursor bound API across files, tables, index cursors, and layered/disaggregated storage. It checks configuration parsing, clear behavior, unsupported cursor types, and compatibility restrictions.

### Important APIs, Types, and Functions
The class inherits from `wtbound.bound_base` and `helper_disagg.DisaggConfigMixin`. It uses `gen_disagg_storages`, `make_scenarios`, `cursor.bound`, `cursor.largest_key`, `cursor.reset`, `open_cursor(..., "next_random=true")`, and helper methods `gen_key`, `gen_val`, and `set_bounds`. Disaggregated scenarios use a leader configuration and skip tiered hooks.

### Control Flow and State
Each scenario creates a WiredTiger object with optional columns, column groups, or an index. The test asserts that calling `cursor.bound()` with no configuration fails, sets lower and upper bounds using either primary keys or index values, clears bounds, and then skips further edge cases for index cursors. Non-index cursors are checked for `largest_key` incompatibility, default `action=set` behavior when only `bound` is provided, invalid action strings, missing bound config, and substring config rejection. For row-store random cursors, bound setting is expected to be unsupported.

### Persistence and Integration
The test creates object metadata but does not require data population except key state on cursors. It integrates with `bound_base` helper generation and disaggregated page-log storage, giving early API coverage for storage backends that might use different cursor implementations.

### Risks and Test Signals
Risks include accepting invalid configs, failing to preserve key state while setting bounds, allowing largest-key or random-cursor combinations that the engine cannot support, and disaggregated/layered cursor inconsistencies. Passing signals baseline API invariants before deeper traversal tests run.
