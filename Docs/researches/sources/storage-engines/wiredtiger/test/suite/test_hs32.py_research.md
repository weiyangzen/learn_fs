# sources/storage-engines/wiredtiger/test/suite/test_hs32.py

Purpose: verifies that no-timestamp updates or deletions clear the relevant history-store records, including cases with and without a long-running transaction.

Important APIs and functions: `test_hs32` covers column, integer-row, and string-row keys; update type scenarios are `deletion` and `update`; long-running transaction scenarios are enabled/disabled. Helpers `create_key`, `get_stat`, and `evict_cursor` support format conversion, stats, and debug eviction.

Control flow: the test writes timestamped versions 1-4 for 10,000 keys, checkpoints and evicts, optionally writes timestamp 5 and opens a long reader at that timestamp, applies no-timestamp changes to even keys, optionally checkpoints/evicts and rolls back the reader, writes all keys at timestamp 10, checkpoints, then validates reads at timestamps 1-4.

State and persistence behavior: even keys touched by no-timestamp changes should no longer expose stale historical content. Odd keys remain historical controls. Deletion mode expects history-store key truncation to occur.

Dependencies and integration points: depends on WiredTiger transaction context manager support from `wttest`, `WT_NOTFOUND`, `stat.conn.cache_hs_key_truncate`, checkpoint, eviction, and history-store cleanup.

Risks and edge cases: the loop applies a transaction to every key but only mutates even keys, increasing runtime. Behavior differs between update and delete modes; only deletion asserts truncation statistics.

Test signals: at read timestamps 1-4, even deleted keys are not found, even updated keys read `value2`, odd keys retain `value1`; deletion scenarios require `cache_hs_key_truncate > 0`.
