<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/misc.c -->
# sources/test-tools/filebench/misc.c

Purpose: provides central logging and process shutdown behavior for Filebench.

Important APIs/functions: `filebench_log(level, fmt, ...)` writes formatted messages to stdout, stderr, or the configured dump file, honoring debug level, `LOG_ERROR1` suppression, `LOG_DUMP`, timestamps relative to `shm_epoch`, and shared `shm_msg_lock` serialization. `filebench_shutdown(error)` marks abort state on error, calls `procflow_shutdown()`, unlinks legacy `/tmp/filebench_shm`, deletes ISM, and exits.

Control flow: logging can be called before `filebench_shm` exists, in which case it treats messages as fatal and prints to stderr. Normal messages are filtered by `shm_debug_level`; dump messages lazily open/truncate `shm_dump_filename` and fsync after each write. Shutdown distinguishes repeated finalization from fresh error aborts using `shm_f_abort`.

State/persistence: uses `filebench_shm` for debug level, dump fd/name, first-error suppression, message lock, epoch, and abort state. Dump files persist on disk if configured; shared memory and ISM are cleaned on shutdown paths.

Dependencies/integration: depends on IPC mutex wrappers, timing helpers, `procflow_shutdown()`, `eventgen`/filesystem includes, and parser line number `lex_lineno` for pre-run syntax errors.

Risks: uses `vsprintf()` into a fixed 128 KiB buffer instead of bounded `vsnprintf()`. Dump file writes ignore write failures except open failure. Shutdown unlinks a hardcoded `/tmp/filebench_shm` path that differs from generated `shmpath` cleanup handled elsewhere.

Test signals: logging before and after `ipc_init()`, debug-level filtering, dump file creation, `LOG_ERROR1` suppression, concurrent logging from workers, and shutdown after both normal and error abort states.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/misc.c -->
