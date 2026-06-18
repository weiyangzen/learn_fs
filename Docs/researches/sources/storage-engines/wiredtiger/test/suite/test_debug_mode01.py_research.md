# sources/storage-engines/wiredtiger/test/suite/test_debug_mode01.py

Purpose: validates `debug_mode=(rollback_error=N)` by forcing simulated `WT_ROLLBACK` errors during inserts and updates, then confirms the setting can be disabled.

Important APIs and control flow: `rollback_error(val, insert=True)` loops through integer keys, begins a transaction, sets key/value, calls either `cursor.insert()` or `cursor.update()`, and uses `assertRaisesException(..., '/WT_ROLLBACK/', True)` to count simulated conflicts. Conflicting operations roll back; successful operations commit.

State and persistence: data lives in `file:test_debug`. The control signal is transactional success versus rollback; no restart is needed.

Dependencies and integration: uses `wiredtiger.WiredTigerError`, transaction APIs, explicit cursor primitives, and `conn.reconfigure`.

Risks and test signals: with rollback errors enabled, total rollbacks across insert/update phases must exceed `entries // 5`. After `debug_mode=(rollback_error=0)`, rollback count must be zero, catching both failure to inject and failure to reconfigure off.
