# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction06.py

Purpose: regression coverage for dirty disaggregated leaves that reconcile to a skip-write single-block replace while ahead of the materialization frontier. Such pages must stay in cache rather than being discarded and later faulted in ahead of the frontier.

Important APIs and functions: `test_layered_eviction06` uses leader disaggregated config, `stat.conn.disagg_block_read_ahead_frontier`, debug eviction transactions, helper `advance_frontier`, page-log `pl_set_last_materialized_lsn`, `conn.set_context_uint`, timestamped writes, checkpoints, and separate read sessions.

Control flow: the test creates a layered table, writes and checkpoints data, manipulates the materialization frontier, triggers eviction with debug cursors, advances frontier at controlled points, and reads back rows. It samples the ahead-frontier block-read statistic to ensure the unsafe fault-in path is not taken.

State and persistence behavior: the key state is a dirty page whose reconciliation can skip writing because the disk image appears replaceable, but whose materialization frontier still makes discard unsafe. Correct behavior retains or restores the page in cache until it is safe.

Dependencies and integration: integrates page-log frontier APIs, dirty page reconciliation, eviction, skip-write replace behavior, and connection statistics. Risks include discarding scrubbed disk images, reading blocks ahead of frontier, stale page restoration, and data loss after eviction. Test signals are exact read assertions, controlled frontier advancement checks, and no unexpected increase in `disagg_block_read_ahead_frontier`.
