# File Research: sources/virtualization/libblockdev/src/utils/logging.c

This file implements shared logging helpers for libblockdev utilities.

State:
- Default log function is `bd_utils_log_stdout`.
- Default log level is `BD_UTILS_LOG_DEBUG` in debug builds and `BD_UTILS_LOG_WARNING` otherwise.

Functions:
- `bd_utils_init_logging()` sets the log callback or disables logging with `NULL`.
- `bd_utils_set_log_level()` changes the threshold.
- `bd_utils_log()` logs a preformatted message if callback and threshold permit.
- `bd_utils_log_format()` formats a printf-style message with `g_vasprintf()` and logs it.
- `bd_utils_log_stdout()` maps syslog-style levels to GLib logging:
  - debug to `g_debug()` only in debug builds,
  - info/notice to `g_info()`,
  - warning/error to `g_warning()`,
  - emergency/alert/critical to `g_critical()`.

Research relevance:
- `exec.c` depends on this for command execution logs.
- Debug logs are compiled out unless the build enables debug.
