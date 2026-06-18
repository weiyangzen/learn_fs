# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable44.py

Purpose: verifies that an uncommitted prepared update evicted to disk has no effect after crash/recovery RTS. It covers column and integer row formats.

Important APIs/types/functions: extends RTS base; defines local `evict` with `debug=(release_evict)` and `ignore_prepare=true`. Uses a second session for the prepared transaction, `prepare_transaction`, `session.checkpoint`, `simulate_crash_restart`, and helper `check`.

Control flow: writes value A to all keys at timestamp 10, opens a second session and prepares an update of the first key at timestamp 20 without committing, evicts the page containing that prepared update, checkpoints, restarts, then checks reads before and after the prepare timestamp.

State and persistence behavior: unresolved prepared update should be ignored/rolled back during recovery; stable/oldest timestamps are deliberately not set. The committed timestamp-10 value remains visible, and prepared value B never appears.

Dependencies and integration points: integrates prepare handling, eviction with ignore-prepare reads, checkpoint, and recovery RTS.

Risks: prepared updates on disk are delicate; failing to ignore unresolved prepare state can expose uncommitted data or fail recovery.

Test signals: empty read at timestamp 5 and value A for all rows at timestamps 15 and 25 after restart.
