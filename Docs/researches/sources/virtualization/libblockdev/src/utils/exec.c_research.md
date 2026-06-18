# File Research: sources/virtualization/libblockdev/src/utils/exec.c

This file implements shared subprocess execution, command logging, progress reporting, utility version checks, and a simple file-write helper.

Global state:
- `id_counter` and `task_id_counter` are protected by mutexes.
- `prog_func` is a global progress callback.
- `thread_prog_func` is thread-local and overrides the global callback.
- Commands are run with environment forced to `LC_ALL=C.UTF-8` and `LANGUAGE` unset.

Command argument handling:
- `_append_extra_args()` appends a NULL-terminated list of `BDExtraArg` option/value pairs to a command argv.
- Empty option or value strings are skipped.
- Extra args are appended after the base argv.

Synchronous capture path:
- `bd_utils_exec_and_capture_output_no_progress()` uses `g_spawn_sync()`.
- Captures stdout/stderr, logs command output, and returns the process exit code through `status`.
- Abnormal process termination is treated as a spawn failure.
- Nonzero normal exit is not itself a function failure in this API; callers inspect `status`.

Error-reporting wrappers:
- `bd_utils_exec_and_report_error()` delegates to progress execution and requires exit code zero.
- `bd_utils_exec_and_report_error_no_progress()` delegates to status-error capture.
- `bd_utils_exec_and_report_status_error()` converts nonzero exit status into `BD_UTILS_EXEC_ERROR_FAILED`.
- `bd_utils_exec_and_capture_output()` requires successful execution and non-empty stdout, otherwise reports either process failure or no-output error.

Progress execution path:
- `_utils_exec_and_report_progress()` uses `g_spawn_async_with_pipes()`.
- Optionally writes a provided input string to stdin.
- Sets stdout/stderr pipes nonblocking.
- Polls both outputs concurrently.
- `_process_fd_event()` reads chunks, splits on newline or NUL, calls a progress extractor callback when supplied, and filters progress lines out of collected output.
- Reports started/progress/finished events through the configured progress callback.
- Waits with `waitpid()` and maps signal death to `128 + signal`.

Version utilities:
- `bd_utils_version_cmp()` compares numeric dotted versions with optional `-R` suffix and rejects unsupported formats.
- `bd_utils_check_util_version()` locates a utility in PATH, runs its version command, extracts a version with an optional regex, and compares it to a minimum.

Progress API:
- `bd_utils_init_prog_reporting()` sets the global callback.
- `bd_utils_init_prog_reporting_thread()` sets the current thread callback.
- `bd_utils_mute_prog_reporting_thread()` suppresses progress in the current thread even if a global callback exists.
- `bd_utils_prog_reporting_initialized()` reflects global/thread callback state.
- `bd_utils_report_started()`, `bd_utils_report_progress()`, and `bd_utils_report_finished()` dispatch progress events.

Other helper:
- `bd_utils_echo_str_to_file()` writes a string to a file with `GIOChannel`, flushes/shuts it down, and prefixes errors with context.

Research relevance:
- This is the central utility path used by many plugins for external commands.
- It deliberately separates “spawn succeeded and status captured” from “command exit code was zero”.
- Locale forcing helps parsers consume predictable command output.
- The progress path treats NUL bytes like line separators for extractor callbacks.
- Command logging includes full argv and captured stdout/stderr.
