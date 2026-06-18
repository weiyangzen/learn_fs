<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/evict-btree-hs.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/evict-btree-hs.py

Purpose: stresses disk access to the WiredTiger history store and eviction by combining a low cache, large values, skewed Pareto access, log-like writes, and long-running transactions.

Important APIs and functions: uses `op_multi_table`, `op_log_like`, `txn`, `sleep`, `Key.KEYGEN_PARETO`, `ParetoOptions`, `Operation.OP_LOG_FLUSH`, `Workload`, and `latency.workload_latency`. No local functions.

Control flow: open a 1 GB cache connection with logging, 12 eviction threads, statistics log, and session cap 800; create one large-value file table; populate 500,000 rows using 40 threads; create a log table; define Pareto search, insert, throttled update, and long transaction threads; define a log flush thread; run 400 search threads, 100 insert threads, 10 update threads, 100 long-transaction threads, and logging thread for 400 seconds.

State and persistence: persistent file table and log table are created. Long transactions keep versions pinned and cause history-store/cache pressure. Logging is enabled for the connection and log table, and latency is written to `latency.out`.

Dependencies and integration: generated from a wtperf configuration and integrates with Workgen runner helpers to emulate wtperf options.

Risks: comments document much larger original wtperf settings; this script is reduced but still resource-heavy. Long transaction expression `txn(((search_op + update_op) * 1000 + sleep(0.1)) * 10000)` can create large operation structures and long pinned histories. Disk usage is explicitly constrained by shortening runtime.

Test signals: populate and workload assertions, statistics log, latency output, and max latency threshold of 50 seconds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/evict-btree-hs.py -->
