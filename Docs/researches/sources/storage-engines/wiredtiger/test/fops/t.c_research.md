<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/t.c -->
# sources/storage-engines/wiredtiger/test/fops/t.c

Purpose: main program for the fops test. It configures a WiredTiger home, runs file-operation stress over both file and table URIs, and handles cleanup/logging.

Important globals/functions: defines `use_txn`, `conn`, `single`, `nops`, `uri`, `config`, `logfp`, and `home`. `main()` parses `-C`, `-h`, `-l`, `-n`, `-r`, `-t`, and `-x`, initializes defaults, creates a work dir path, installs SIGINT handler, then for each run and each configured URI calls `shutdown()`, `wt_startup()`, `fop_start()`, and `wt_shutdown()`. `wt_startup()` recreates the home and opens WiredTiger with small cache, statistics, and statistics log. Event handlers suppress expected missing-file/bulk/forced-checkpoint messages.

State and persistence: creates/removes the test home each run, writes optional log file, and emits statistics logs on close via WiredTiger config.

Dependencies and integration: works with `fops.c` and `fops_file.c`; uses WiredTiger public API, internal test helpers, signal handling, and pthread rwlock.

Risks and test signals: `shutdown()` removes the home before every URI, so file/table runs are isolated. Infinite runs are possible with `-r 0`. Signal cleanup removes the home, which can erase failure evidence on interrupt. Expected error filtering must stay aligned with fops race behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/t.c -->
