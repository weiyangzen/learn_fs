# sources/storage-engines/wiredtiger/test/suite/test_checkpoint37.py

Purpose: verifies reconciliation during checkpoint removes obsolete updates from pages and keeps cache memory growth bounded.

Important APIs and types: `eviction=[skip_update_obsolete_check=true]`, timestamped `large_updates`, `stat.conn.cache_bytes_inuse`, `stat.conn.cache_obsolete_updates_removed`, and checkpoint.

Control flow: write initial data at timestamp 5, set oldest/stable, checkpoint and reopen, perform repeated full-table updates at timestamps 10, 20, 30, and 40; after advancing oldest/stable to each new timestamp, checkpoint and compare cache bytes with an earlier baseline; finally assert obsolete-update removal statistic is positive.

State and persistence behavior: as oldest advances, older update chains become obsolete. Checkpoint reconciliation should discard obsolete updates and avoid unbounded cache growth.

Dependencies and integration points: interacts with eviction configuration, cache statistics, timestamp advancement, and checkpoint reconciliation. Covers row/column stores.

Risks: contains `self.session.breakpoint()`, which may be test-harness specific and surprising. Cache byte thresholds are heuristic (`< prev * 2`).

Test signals: cache bytes after each checkpoint stay below twice baseline and `cache_obsolete_updates_removed` is greater than zero.
