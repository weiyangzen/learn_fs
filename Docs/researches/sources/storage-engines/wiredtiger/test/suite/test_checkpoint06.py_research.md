# sources/storage-engines/wiredtiger/test/suite/test_checkpoint06.py

Purpose: verifies rollback-to-stable rolls back a truncate committed after the stable timestamp, including prepared-transaction and non-prepared variants.

Important APIs/types/functions: `make_scenarios`, `session.truncate`, `prepare_transaction`, `timestamp_transaction`, `rollback_to_stable`, `reopen_conn`, and row/column formats.

Control flow: insert 10,000 rows at timestamp 2, set stable to 2, reopen to flush to disk, truncate from key 5 to the end at timestamp 3, optionally prepare with durable timestamp 5 while stable is 4, write another table at timestamp 6 to trigger eviction, checkpoint, call `rollback_to_stable`, and verify every original row remains.

State/persistence behavior: the truncation is beyond stable and must be undone even if it was included in a checkpoint or had a durable timestamp later than stable. Auxiliary table writes increase eviction/checkpoint pressure.

Dependencies/integration: truncate, timestamps, prepared transactions, checkpoint, eviction pressure, RTS.

Risks/test signals: failure is missing rows after RTS. The prepared path specifically checks commit/durable timestamp ordering.
