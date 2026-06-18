# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable15.py

Purpose: tests runtime RTS on fixed-size or integer-style values, ensuring unstable updates are aborted and older stable integer values remain visible. Scenarios include column/integer-row keys, in-memory/disk, and worker counts.

Important APIs/types/functions: class derives directly from `wttest.WiredTigerTestCase`, adds `verify_rts_logs` teardown, and defines a local `check` method. It uses `session.create`, cursor item assignment, timestamped commits, `conn.set_timestamp`, `conn.rollback_to_stable`, and `stat.conn.txn_rts_upd_aborted`/`txn_rts`.

Control flow: creates a table with the scenario key/value format, pins timestamps at 1, inserts value `0x20` at timestamp 2, updates to `0x30` at 5, rolls back to stable 2, checks only the first value remains, then writes further updates at 7 and 9, rolls back to stable 7, and checks the timestamp-7 value remains.

State and persistence behavior: intentionally performs two RTS passes on one table to verify state can be rolled back, updated again, and rolled back again. In-memory mode adds `in_memory=true`; disk mode uses normal persisted tables.

Dependencies and integration points: uses low-level cursor writes rather than the common base helpers, but still integrates with RTS log verification and statistics.

Risks: the source reassigns `value30` before defining `value40`, which is intentional-looking but confusing; report consumers should verify this if changing the test. Fixed-size column behavior can differ from string-value tests.

Test signals: local `check` verifies row counts and values at read timestamps. Stats expect two RTS calls and `(nrows * 2) - 2` aborted updates after the second pass.
