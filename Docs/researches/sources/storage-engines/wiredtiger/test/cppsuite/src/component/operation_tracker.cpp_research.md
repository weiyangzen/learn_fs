# sources/storage-engines/wiredtiger/test/cppsuite/src/component/operation_tracker.cpp

Purpose: Tracks schema and row operations in logged WiredTiger tables and periodically sweeps obsolete row-operation history.

Important APIs/types/functions: constructor builds operation tracking table config from configured key/value formats. `load` creates schema and operation tracking tables, opens cursors, and creates a dedicated sweep session/cursor. `do_work` scans the operation table backwards, finds globally visible updates per collection/key at or before oldest timestamp, and removes older obsolete records in no-timestamp transactions. `save_schema_operation`, `save_operation`, and `set_tracking_cursor` persist create/delete and row operation metadata.

Control flow: schema operations are restricted to create/delete; row operation saves reject schema events. Sweeping only runs for the default operation table schema, preserving user-defined validation data for custom schemas.

State and persistence: persists `table:schema_tracking` and `table:operation_tracking` with logging enabled. In-memory state includes sessions/cursors, table config, compression flag, and timestamp manager reference.

Dependencies/integration: depends on `connection_manager`, `timestamp_manager`, constants, `scoped_session/cursor`, and `test_util`; database and workload operations call into it.

Risks and test signals: sweep logic assumes reverse ordering by collection/key/timestamp and default key/value formats. It uses `volatile` running state from `component`. Any unexpected cursor error is fatal; trace logs show obsolete/global update decisions.
