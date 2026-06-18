# File Research: sources/os/bsd/openbsd-src/sbin/unwind/log.c

`log.c` implements unwind's local logging wrapper. `uw_log_init()` records debug/verbose mode, initializes the process name, opens syslog when not debugging, and calls `tzset()`.

The normal logging path is `logit()`/`vlog()`: in debug mode messages are printed to stderr with a trailing newline, otherwise they go to syslog. `uw_log_warn()` preserves `errno`, appends `strerror(errno)` to the caller's message, and falls back cleanly if `asprintf()` fails. `log_warnx()`, `uw_log_info()`, and `log_debug()` provide error-free, info, and verbosity-gated debug wrappers.

Fatal paths use `vfatalc()` to format `"fatal in <proc>"` messages with or without an errno code, then `fatal()` and `fatalx()` exit with status 1. Global state is limited to debug/verbose flags and the current process name.
