# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/log.c

Small daemon logging implementation used by `slaacd`.

Behavior:
- `log_init()` chooses stderr logging in debug mode or syslog otherwise, initializes process name, and calls `tzset()`.
- `log_procinit()` changes the process label used in fatal messages.
- `log_setverbose()` / `log_getverbose()` manage runtime verbosity.
- `vlog()` preserves `errno`, writes to stderr in debug mode, or syslog otherwise.
- `log_warn()` appends `strerror(errno)` while preserving the original errno.
- `log_warnx()`, `log_info()`, and `log_debug()` are level-specific wrappers.
- `fatal()` and `fatalx()` log critical errors with process context and exit.

Robustness notes:
- Handles `asprintf()` failure with best-effort direct `vfprintf()`.
- Preserves `errno` across logging calls.
