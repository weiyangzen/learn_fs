<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare_evict_reconcile.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare_evict_reconcile.py

Purpose: prepared transaction workload tuned to force eviction/reconciliation pressure. It uses large keys/values, small leaf pages, low cache target, and timestamped prepared writes.

Important APIs and functions: Workgen APIs for `Operation.OP_SEARCH`, `OP_INSERT`, `OP_UPDATE`, `txn`, transaction timestamp flags, and latency output. It uses direct WT table configuration for page size and allocation.

Control flow: open a 500 MB cache connection with `eviction_target=60`; create one table with 4 KB leaves and 7 KB values; populate 5,000 rows; build read timestamp lag 300 readers, prepared insert writers, and commit timestamp updaters, each repeated 5,000 times; run 30 copies of each for 300 seconds with oldest lag 400 and stable lag 20.

State and persistence: writes large page images and history to a file table, advances timestamps, and writes `latency.out`. No explicit checkpoint thread is configured; normal WT behavior applies.

Dependencies and integration: extends `example_prepare.py` toward cache/eviction behavior. Useful as a smaller reproducer for prepared reconciliation paths.

Risks: final workload return is not asserted. Large values with small leaf pages can create intense cache pressure. Report interval exceeds runtime, limiting progress visibility.

Test signals: populate console messages, successful workload completion, timestamp behavior, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare_evict_reconcile.py -->
