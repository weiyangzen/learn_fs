# Research: sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.c

## sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.c

Purpose: Main driver for the checkpoint stress test executable.

Important functions/APIs: global `GLOBAL g`, `init_thread_data`, `main`, `wt_connect`, `wt_shutdown`, `cleanup`, event handlers, `log_print_err_worker`, `type_to_string`, and `usage`.

Control flow: `main` initializes defaults, parses options for table type/count, workers, operations, timestamps, precise checkpoint, prepare, replay, stress failpoints, cache config, verify-only, disagg, and home. It enforces option combinations, initializes random seeds and work directory, configures disagg requirements, then runs one or more iterations: cleanup, allocate cookies/table URIs, allocate thread data, connect, optionally verify-only with prepare discover, otherwise start service threads and workers, stop/join threads, free arrays, and close WT. Signal handling calls cleanup and exits.

State and persistence: owns global configuration, WT home, connection, table cookies, thread data, timestamps, prepared id, status, log file, and running flag. `wt_connect` builds the WT open config with logging, stats, cache/eviction settings, timing stress, sweep config, precise checkpoint/preserve prepared, tiered setup, and testutil open. `wt_shutdown` closes the connection and tiered hooks.

Dependencies/integration: integrates testutil option parsing, worker/checkpointer modules, WiredTiger public API, disagg/tiered utilities, and CMake variants. Risks include global mutable state, complex option interactions, fixed config buffer sizes, and cleanup after partial failures. Test signals are process exit status, stdout milestones, and logged errors.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/test_checkpoint.c -->
