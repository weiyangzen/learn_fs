# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable33.py

Purpose: tests RTS behavior for logged versus non-logged tables in an in-memory connection. Logged objects should not be rolled back the same way as non-logged objects.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `conn_config = 'in_memory=true,verbose=(rts:5)'`, `verify_rts_logs`, `SimpleDataSet`, timestamped cursor writes, `conn.set_timestamp`, and `conn.rollback_to_stable`.

Control flow: creates a table with scenario-selected logging, writes changes at timestamp 30, sets stable to 20, runs RTS, opens a cursor, and checks whether values are the updated values or original dataset values depending on the logging flag.

State and persistence behavior: in-memory plus logging creates a special persistence/rollback boundary. Non-logged updates should be rolled back; logged updates should remain.

Dependencies and integration points: integrates dataset setup, logging configuration, and in-memory connection RTS behavior.

Risks: semantics are table-config dependent; incorrect scenario config can invert expectations. The test is small but covers a behavior not exercised by ordinary disk-backed tables.

Test signals: direct cursor value assertions for keys 10-12, choosing either updated values or original values based on `logged`.
