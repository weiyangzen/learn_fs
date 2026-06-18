# sources/storage-engines/wiredtiger/test/suite/test_checkpoint38.py

Purpose: validates parallel checkpoint worker threads reconcile pages during a large checkpoint and that related statistics are populated.

Important APIs and types: `checkpoint_threads` connection configuration, `stat.conn.checkpoint_pages_reconciled`, `checkpoint_parallel_pages_reconciled`, `checkpoint_sync_rec_pct`, and statistics logging.

Control flow: run scenarios with 4 and 8 checkpoint threads, create a table with 55,000 large records and small leaf pages, sample checkpoint stats, run checkpoint, compute deltas, print metrics, and assert reconciliation happened in both total and parallel-worker counters.

State and persistence behavior: a large cache and disabled pre-checkpoint scrubbing keep dirty pages in cache until the checkpoint walk. The test is about checkpoint execution distribution, not data scan validation.

Dependencies and integration points: uses connection-level checkpoint threading, eviction tuning, statistics cursors, and statistics log configuration. It can run under tiered hook because cache is enlarged for that overhead.

Risks: data volume is about hundreds of MB and can be resource-heavy. If eviction writes dirty pages before checkpoint, parallel counters may be low.

Test signals: total pages reconciled, parallel pages reconciled, and checkpoint sync reconciliation percentage are all greater than zero.
