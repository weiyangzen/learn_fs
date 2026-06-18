# sources/storage-engines/wiredtiger/test/format/t.c

Purpose: main entry point for the format test program. It parses command-line/config input, initializes global process state, creates or reopens the database, drives load/verify/read-scan/operation phases, and handles shutdown, salvage, tracing, and failure reporting.

Important APIs and functions: `main`, `format_process_env`, `set_alarm`, `locks_init`, `locks_destroy`, `format_die`, and `usage`. It coordinates `config_*`, `path_setup`, `disagg_setup/teardown`, `wts_*`, `timestamp_*`, `tables_apply`, `operations`, `trace_*`, and `wts_salvage`.

Control flow: process setup installs signal handlers and RNGs, parses options `-B -C -c -h -q -R -S -T -v`, loads config, configures RNGs and disaggregated processes, runs `config_run`, creates/reopens WiredTiger, initializes timestamps, discovers prepared transactions, initializes key/value data, bulk-loads when new, verifies, optionally read-scans, starts checkpointing, runs three operation phases or disagg leader/follower switch phases, dumps stats, verifies again, closes, salvages, tears down tracing/disagg, prints success, and clears config.

State and persistence: defines global `GLOBAL g`, `TABLE *tables[]`, and `ntables`. It owns home paths, reopen behavior, process-level locks, signal timers, and database lifecycle. It writes `CONFIG`, stats, trace dirs, database files, and possible salvage artifacts through called modules.

Dependencies and integration: top-level integration point for all format modules and the test utility library. It also depends on WiredTiger version macros for backward compatibility and on external harness behavior that scans output strings.

Risks and test signals: some output strings are harness contracts, notably process running, alarm timeout, abort-to-test-recovery, run FAILED, and successful completion. Error handling intentionally serializes on `g.death_lock`, disables trace/progress, prints config, and sleeps before teardown to expose failures.
