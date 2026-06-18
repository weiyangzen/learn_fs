# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable27.py

Purpose: validates RTS with a no-timestamp update over timestamped RLE-like content. Only the non-timestamped key should remain visible after rollback.

Important APIs/types/functions: extends the RTS base; defines local `evict` using `debug=(release_evict)`. Uses `large_updates`, explicit no-timestamp transaction, `conn.rollback_to_stable`, and direct cursor iteration.

Control flow: writes all rows at timestamp 20, evicts to force reconciliation, performs a no-timestamp update for key 7, sets stable to 15, runs RTS, then scans at multiple read timestamps and expects only key 7 with the no-timestamp value.

State and persistence behavior: no-timestamp updates are globally visible and must survive even when all timestamped updates are newer than stable. In-memory/disk and worker thread scenarios cover both storage modes.

Dependencies and integration points: depends on the shared base, debug eviction, and WiredTiger's semantics for no-timestamp updates mixed with timestamped content.

Risks: RLE assumptions are noted in source comments as not directly asserted. If reconciliation does not form the expected shape, coverage weakens but the visible behavior remains checked.

Test signals: cursor scan after RTS asserts the only visible key is 7 and its value is the no-timestamp value, across all checked timestamps.
