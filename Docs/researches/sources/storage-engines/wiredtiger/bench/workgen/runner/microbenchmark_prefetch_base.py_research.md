<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_base.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_base.py

Purpose: shared base class for prefetch verification microbenchmarks. It centralizes database setup, population, and prefetch-related statistics collection.

Important APIs and functions: class `microbenchmark_prefetch` with `__init__`, `populate`, and `print_prefetch_stats`. It uses `wiredtiger.stat.conn.block_read` and `cache_read_app_count`, `Context`, `Table`, `Operation.OP_INSERT`, `Thread`, and `Workload`.

Control flow: constructor opens a 1 GB cache connection with 12 eviction threads, statistics for all/file sources, and `prefetch=(available=true,default=false)`; creates one `table:test_prefetch0` file table with key size 12 and value size 138; `populate` inserts 12,000,000 rows; `print_prefetch_stats` opens a statistics cursor, prints block/cache-read counters, and writes `prefetch_stats.out`.

State and persistence: creates a large single table and statistics artifacts in the WT home. The class stores `context`, `conn_config`, `conn`, `session`, `nrows`, `table`, and optional `workload`.

Dependencies and integration: imported by `microbenchmark_prefetch_off_verify.py` and `microbenchmark_prefetch_on_verify.py`. Depends on WiredTiger prefetch configuration and stats IDs.

Risks: 12 million rows can be slow/heavy. `print_prefetch_stats` writes only blocks read to file while printing both counters, so downstream tools may miss `cache_read_app_count`. File handle is manually closed but would benefit from context manager.

Test signals: populate assertion, printed statistics, and `prefetch_stats.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_base.py -->
