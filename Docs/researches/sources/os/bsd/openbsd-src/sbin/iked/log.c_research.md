# File Research: sources/os/bsd/openbsd-src/sbin/iked/log.c

Read completely: 218 lines.

Implements iked's small logging facade over stderr/syslog, with debug/verbose controls and fatal helpers.

Core behavior:
- Global `debug` selects stderr logging versus syslog; global `verbose` gates `log_debug()`.
- `log_init()` records debug mode, sets verbose to debug by default, initializes the process name from `__progname`, opens syslog when not debugging, and calls `tzset()`.
- `log_procinit()`, `log_setverbose()`, and `log_getverbose()` update/read logging state.
- `logit()` forwards variadic messages to `vlog()`.
- `vlog()` preserves `errno`, writes a newline-terminated message to stderr in debug mode using best-effort `asprintf()`, or sends the message to syslog otherwise.
- `log_warn()` preserves `errno`, appends `strerror(saved_errno)` to the caller message, and has fallback behavior if formatting allocation fails.
- `log_warnx()`, `log_info()`, and `log_debug()` emit fixed-priority messages; debug messages only emit when `verbose > 1`.
- `vfatalc()` formats fatal messages with optional errno text and `log_procname`.
- `fatal()` logs with current `errno` then exits, while `fatalx()` logs without errno then exits.

Risks and notes:
- The code intentionally restores `errno` after logging paths.
- `log_procname` is global and expected to be initialized before fatal messages.
