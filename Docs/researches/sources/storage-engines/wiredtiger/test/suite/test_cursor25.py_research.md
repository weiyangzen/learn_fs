## sources/storage-engines/wiredtiger/test/suite/test_cursor25.py

### Purpose
`test_cursor25.py` tests `debug=(dump_version=(show_prepared_rollback=true))` behavior for in-memory B-trees. It verifies when rolled-back prepared values should be emitted by the version cursor and when tombstone-only rollback artifacts should remain hidden.

### Important APIs, Types, and Functions
The test uses `WiredTigerTestCase`, `make_scenarios` for row and variable column stores, `wiredtiger.WT_NOTFOUND`, and version cursor debug configuration flags `enabled`, `visible_only`, and `show_prepared_rollback`. Constants model special transaction states: `WT_TXN_ABORTED`, `WT_TS_MAX`, `PREPARE_TS`, and `ROLLBACK_TS`. Helpers include `create`, `open_version_cursor`, `prepared_insert_rollback`, `verify_value`, and `verify_prepare_rollback_value`.

### Control Flow and State
The file creates in-memory, non-logged tables so rolled-back prepared updates remain inspectable. Tests cover: rolled-back prepared insert with no later write; rolled-back insert followed by committed insert; rolled-back overwrite over a committed value; rolled-back prepared delete; rolled-back insert followed by multiple committed updates; insert-then-delete within the same prepared transaction; and explicit `visible_only=false` with `show_prepared_rollback=true`. The final test opens a non-in-memory object and expects an error because the feature is in-memory-only.

### Persistence and Integration
State is transactionally timestamped but configured `in_memory=true,log=(enabled=false)`. The tests integrate with the debug version cursor and validate update-chain metadata including aborted transaction markers and rollback timestamps stored in the durable timestamp field.

### Risks and Test Signals
The covered risks are over-reporting rollback tombstones, under-reporting rolled-back values, wrong ordering relative to committed versions, and allowing unsupported on-disk use. Passing confirms callers such as diagnostic or drain tooling can opt into seeing useful rolled-back prepared values without corrupting normal visible-only behavior.
