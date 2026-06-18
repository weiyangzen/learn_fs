# File Research: sources/local-fs/dlm/dlm_sand/log.c

This file implements asynchronous logging for `dlm_sand`.

Key state:
- `log_dump`: in-memory circular dump buffer for query responses.
- `log_ents`: circular array of pending entries for file/syslog output.
- Mutex and condition variable protect logging state.
- A background thread drains entries and writes to logfile/syslog.
- `log_dropped` counts messages dropped when the pending-entry ring is full.

Key behavior:
- `setup_logging()` initializes priorities, stderr behavior, opens `LOG_FILE_PATH`, allocates the entry ring, calls `openlog()`, and starts the log thread.
- `log_level()` formats timestamped messages, stores every message in the dump ring, queues messages meeting logfile/syslog thresholds, optionally writes to stderr, and signals the logging thread.
- `copy_log_dump()` copies the circular dump buffer under the log mutex.
- `log_thread_fn()` waits for pending entries, writes dropped-entry notices, and calls `write_entry()`.
- `close_logging()` signals shutdown, joins the thread, closes syslog and logfile.
- `set_logfile_priority()` raises logfile verbosity to debug when `debug_logfile` is enabled.

Important dependencies:
- Uses options from `sand_internal.h`: `daemon_debug`, `debug_logfile`, and logging priority globals.
- Uses macros from `log.h` for callers.
- Query handling outside this group can expose the dump buffer.

Notable details:
- This logger is more thread-friendly than `dlm_controld/logging.c`: formatting and queueing are mutex-protected, while file/syslog writes happen in a worker thread.
- If the log entry ring fills, messages are dropped but a later “dropped N entries” notice is written.
- `write_dropped()` formats without a newline, unlike normal log entries.
