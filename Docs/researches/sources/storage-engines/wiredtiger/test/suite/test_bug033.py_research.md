# sources/storage-engines/wiredtiger/test/suite/test_bug033.py

Purpose: regression for WT-12096, testing insertion of obsolete updates on an update chain after rollback to stable, with checkpoint and eviction racing.

Important APIs/types/functions: `wiredtiger`, `wtthread.checkpoint_thread`, `stat.conn.checkpoint_state`, `timing_stress_for_test=[checkpoint_slow]`, helper `evict`, timestamp APIs, and `rollback_to_stable`.

Control flow: create timestamped updates at 2 and 4, evict to disk, roll back to stable at 1, insert a new timestamp-2 update, advance oldest/stable to 3 making tombstone/update obsolete, sleep to let oldest ID advance, insert timestamp-4 update, start a slow checkpoint thread, wait for checkpoint state to become active, then evict the key while checkpointing.

State/persistence behavior: constructs a chain with obsolete tombstone/update entries plus an on-disk newer value, then forces reconciliation under checkpoint concurrency. The focus is correct obsolete update insertion/removal without corrupting chain state.

Dependencies/integration: timestamp manager, rollback-to-stable, eviction, checkpoint thread, stats cursor, and timing stress.

Risks/test signals: no final assertions; pass condition is no crash/assertion or incorrect busy/error during the concurrent eviction/checkpoint path.
