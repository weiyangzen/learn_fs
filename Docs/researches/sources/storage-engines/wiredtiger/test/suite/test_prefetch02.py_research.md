# sources/storage-engines/wiredtiger/test/suite/test_prefetch02.py

## Purpose
Runs traversal and verify scenarios expected to trigger prefetch, and confirms statistics move only when prefetch is enabled.

## APIs, Types, And Functions
Defines `PrefetchStats` and `test_prefetch02`, mixing in `suite_subprocess`. It uses connection/session prefetch configs, statistics `prefetch_pages_queued`, `prefetch_attempts`, `prefetch_attempts_succeeded`, `prefetch_pages_read`, `verifyUntilSuccess`, and large fixed-page datasets.

## Control Flow, State, And Persistence
The test copies the home, opens a setup connection with selected config, populates 100,000 rows in a small-page file, checkpoints, closes to clear cache, and reopens. Traversal scenarios walk half the keyspace, snapshot stats, finish forward or backward traversal, then assert stats increased or remained zero. Verify scenarios run verification and assert the same prefetch/stat behavior.

## Dependencies, Integration, Risks, And Test Signals
Depends on disk reads rather than cache hits, small page layout, prefetch worker activity, and statistics. Risks are flaky nondecreasing stats, unavailable prefetch incorrectly doing work, or verify not using prefetch. Signals are stat snapshots and zero-stat assertions; some checks use `GreaterEqual` pending stronger WT-12193 assertions.
