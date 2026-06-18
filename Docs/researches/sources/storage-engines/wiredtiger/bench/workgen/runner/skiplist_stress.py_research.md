<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/skiplist_stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/skiplist_stress.py

Purpose: stress workload for skiplist-related insertion paths with small cache and debug stress enabled.

Important APIs and functions: uses `debug_mode=(stress_skiplist=1)`, `split_deepen_min_child`, Workgen inserts, thread multiplication, and latency output.

Control flow: open a 100 MB cache connection with logging disabled, fast statistics, JSON stats log, and skiplist debug stress; create `file:test`; set key size 64, value size 10, and range 100 million; run 50 insert threads for 360 seconds.

State and persistence: creates one file table and appends/inserts random-range keys under heavy concurrency. Writes `latency.out`.

Dependencies and integration: tests WiredTiger debug mode behavior and split/skiplist concurrency.

Risks: debug mode option requires a compatible build. Small cache with many threads may trigger stalls or non-representative performance. No populate phase means table growth happens only during run.

Test signals: workload assertion, statistics log, latency file, and absence of split/skiplist failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/skiplist_stress.py -->
