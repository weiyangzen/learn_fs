# File Research: sources/local-fs/dlm/dlm_controld/logging.c

This file implements synchronous logging for `dlm_controld`: syslog, optional logfile, stderr in debug mode, and in-memory circular dump buffers.

Key behavior:
- `init_logging()` sets default syslog/logfile priorities, creates log directories with restrictive permissions, opens the logfile, marks it close-on-exec, and calls `openlog()`.
- `close_logging()` closes syslog and logfile state.
- `set_logfile_priority()` raises logfile verbosity to `LOG_DEBUG` when `debug_logfile` is enabled.
- `log_level()` formats messages with monotonic timestamp and optional lockspace/name prefix.
- General messages are saved into `log_dump`; plock-tagged messages are also saved into `log_dump_plock`.
- `copy_log_dump()` and `copy_log_dump_plock()` copy circular-buffer contents for daemon query replies.

Important dependencies:
- Uses daemon options through `opt()` and `dlm_options`.
- Uses constants from daemon headers: `DEFAULT_SYSLOG_FACILITY`, `DEFAULT_SYSLOG_PRIORITY`, `DEFAULT_LOGFILE_PRIORITY`, `DEFAULT_LOGFILE`, `LOG_DUMP_SIZE`, `LOG_PLOCK`, `LOG_NONE`.
- Query serving in `main.c` exposes these buffers through `DLMC_CMD_DUMP_DEBUG` and `DLMC_CMD_DUMP_LOG_PLOCK`.

Notable details:
- Logging is not internally mutex-protected here; `main.c` serializes daemon/query access with `query_mutex` for many paths, but general signal/thread interactions should be understood in that context.
- The logfile timestamp uses wall clock, while message body starts with monotonic time.
