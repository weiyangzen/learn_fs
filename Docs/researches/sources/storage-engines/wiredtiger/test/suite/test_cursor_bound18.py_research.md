## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound18.py

### Purpose
`test_cursor_bound18.py` checks column-group bound rollback semantics. When setting a bound on one underlying column group fails, the original primary/table bounds must remain intact rather than leaving a partially updated state.

### Important APIs, Types, and Functions
The class derives from `bound_base`, forces `use_colgroup=True` and `uri='table:'`, and expands over key/value formats, inclusivity/eviction configs, and direction. It uses `create_session_and_cursor`, `set_bounds`, `cursor_traversal_bound`, and `assertRaisesWithMessage`.

### Control Flow and State
The test creates a column-group-backed table and sets initial lower 40 and upper 90. Attempts to set an upper bound below the lower bound and a lower bound above the upper bound must fail. It then successfully sets lower 50 and upper 80 and validates traversal. A later failed upper-bound change to 40 should not destroy prior bound state; traversal from an explicitly set key validates the expected retained range. It successfully narrows upper to 70, then a failed lower change to 80 must leave the 50-70 range intact. Final successful setting of both bounds confirms the cursor remains usable.

### Persistence and Integration
The important integration point is propagation from a table cursor to its column-group cursors. Persistent data comes from `bound_base`.

### Risks and Test Signals
The risk is partial state corruption when multi-cursor bound propagation fails. Passing confirms failures are atomic from the caller’s perspective and previous bounds remain valid.
