# File Research: sources/local-fs/gfs2-utils/gfs2/include/logging.h

This header defines simple logging macros gated by a global `print_level`.

It declares verbosity controls and message levels from debug through critical:
- `increase_verbosity()`, `decrease_verbosity()`
- `MSG_DEBUG`, `MSG_INFO`, `MSG_NOTICE`, `MSG_WARN`, `MSG_ERROR`, `MSG_CRITICAL`, `MSG_NULL`
- `log_debug`, `log_info`, `log_notice`, `log_warn`, `log_err`, `log_crit`

`log_debug()` prefixes messages with function name and line number. Info/notice/warn write to stdout, while error/critical write to stderr.

Risks and notes:
- The macros rely on GNU variadic macro syntax.
- There is no synchronization or structured logging; output ordering is suitable for single-process CLI tools.
- Callers must define `print_level` exactly once elsewhere.
