# sources/storage-engines/wiredtiger/test/suite/test_isolation01.py

Purpose: tests transaction isolation-level restrictions for writes and `session.reset_snapshot`.

Important APIs and functions: scenarios cover `read-uncommitted`, `read-committed`, and `snapshot`. The test uses `begin_transaction('isolation=...')`, cursor `insert`, `reset_snapshot`, and expected error regexes.

Control flow: it creates a string table, begins a transaction at the scenario isolation level, attempts an insert, expecting failure for read-uncommitted/read-committed and success for snapshot. It then calls `reset_snapshot`, expecting failure after snapshot writes and unsupported-isolation failure for read-committed/uncommitted. A second transaction searches a key and verifies `reset_snapshot` succeeds only for snapshot read-only state.

State and persistence behavior: transaction state transitions matter more than durable persistence. `reset_snapshot` is legal only before modifications in snapshot isolation and unsupported in weaker isolation modes.

Dependencies and integration points: depends on WiredTiger transaction isolation rules, cursor write validation, and reset-snapshot API error reporting.

Risks and edge cases: exact error text regexes may need updates if diagnostics change. The snapshot second transaction searches without asserting search result, focusing only on reset legality.

Test signals: writes fail/succeed per isolation mode, and `reset_snapshot` raises or succeeds according to transaction state.
