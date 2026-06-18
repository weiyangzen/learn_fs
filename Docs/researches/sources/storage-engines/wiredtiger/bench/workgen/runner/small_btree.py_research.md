<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree.py

Purpose: basic small btree read workload.

Important APIs and functions: uses `Context`, `Session.create`, `Table`, insert/search `Operation`, `Thread`, and `Workload`.

Control flow: open 500 MB cache; create `file:test.wt`; populate 500,000 rows; run 8 search threads for 120 seconds with 5-second reports.

State and persistence: creates one file table in the WT home. No explicit latency or close call.

Dependencies and integration: simple benchmark/smoke workload for read performance over a small table.

Risks: no latency output, so observability is limited to Workgen reports. Table remains in the home until context cleanup.

Test signals: populate and workload assertions plus read throughput report.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree.py -->
