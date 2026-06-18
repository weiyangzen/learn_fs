<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_txn.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/example_txn.py

Purpose: simple transactional write example. It populates a table and then mixes readers with transaction-wrapped two-operation insert writers.

Important APIs and functions: uses `txn(opwrite * 2)` to wrap repeated insert operations in a Workgen transaction. Other APIs are `Context`, `Table`, `Operation`, `Thread`, `Workload`.

Control flow: open a 500 MB cache database; create one string table; populate 500,000 rows; create one search thread and one transaction-wrapped double-insert writer; run eight readers and two writers for 10 seconds with 5-second reports.

State and persistence: table content persists in the WT home and grows during the write workload. No explicit timestamps, checkpoints, or latency files are used.

Dependencies and integration: demonstrates `runner.core.txn` and Workgen transaction grouping. Useful as a smoke test for transaction support.

Risks: append inserts after a large populate can be resource-sensitive. Without timestamp or isolation config, semantics are default transaction behavior.

Test signals: populate and workload assertions plus periodic report output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_txn.py -->
