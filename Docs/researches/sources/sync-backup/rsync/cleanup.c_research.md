# sources/sync-backup/rsync/cleanup.c

Purpose: central end-of-run and interrupted-transfer cleanup.

Important APIs/types/functions: public `close_all()`, `_exit_cleanup()`, `cleanup_disable()`, `cleanup_set()`, `cleanup_set_pid()`; globals `called_from_signal_handler`, `shutting_down`, `flush_ok_after_signal`, `cleanup_got_literal`, and `cleanup_child_pid`.

Control flow: `_exit_cleanup()` is a reentry-safe switch state machine using `case_N.h`. It preserves first exit info, waits on cleanup child, preserves partial files when configured, flushes IO, unlinks temp files, removes pid file, derives final exit code from IO flags, logs exit, sends error-exit messages, drains IO, sleeps for daemon errors, closes sockets/files, and exits or `_exit`s when in a signal handler.

State and persistence: tracks current temp/target file and fds. Persistent effects include partial-file finalization, temp-file deletion, pid-file removal, and process termination.

Dependencies/integration: touches transfer finalization, IO messaging, logging, signal handling, daemon config, and process management.

Risks: cleanup can be invoked recursively or from signal context; switch-step discipline is critical. Wrong partial handling can lose resumable data.

Test signals: integration tests, valgrind, coverage, and signal/timeout paths exercise this indirectly.
