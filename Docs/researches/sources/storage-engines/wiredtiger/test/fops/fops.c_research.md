<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/fops.c -->
# sources/storage-engines/wiredtiger/test/fops/fops.c

Purpose: thread driver for the fops stress test. It spawns worker threads that randomly execute WiredTiger file operations and reports per-thread operation counts and throughput.

Important types/functions: local `STATS` records counts for bulk, unique bulk, checkpoint, create, unique create, cursor, drop, and verify operations. `fop_start(nthreads)` allocates `run_stats` and thread IDs, starts workers with `__wt_thread_create`, joins them, computes elapsed seconds, prints stats and ops/sec, and frees memory. `fop(void *arg)` initializes a random state and runs `nops` iterations, randomly choosing among object operation functions. `print_stats()` aggregates unique/non-unique bulk and create counts in output.

State and persistence: `run_stats` is process-global for the run. Worker operations mutate the WiredTiger home via functions in `fops_file.c`.

Dependencies and integration: includes `thread.h`, using global `nops`, operation prototypes, WiredTiger thread helpers, random helpers, and test allocation/check helpers.

Risks and test signals: switch uses `% 9` but has cases 0-7, so one random value performs no operation while still consuming an iteration. Operation failures are handled in callee functions. Throughput division assumes nonzero elapsed time.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/fops.c -->
