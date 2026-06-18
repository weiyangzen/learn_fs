# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/log.c

## Purpose
`log.c` provides `dhcpleased` logging, debug output, verbosity control, warning helpers, and fatal-exit helpers.

## Main Responsibilities
- Initializes logging to stderr in debug mode or syslog otherwise.
- Tracks process name for fatal messages.
- Tracks verbosity for debug logging.
- Preserves `errno` across logging calls.
- Provides formatted warning helpers with or without `strerror(errno)`.
- Provides fatal helpers that log and exit.

## Important APIs
- `log_init`
- `log_procinit`
- `log_setverbose`
- `log_getverbose`
- `logit`
- `vlog`
- `log_warn`
- `log_warnx`
- `log_info`
- `log_debug`
- `fatal`
- `fatalx`

## Integration Notes
All daemon processes use this module. In debug mode it appends a newline and writes to stderr; otherwise it logs through syslog.

## Risk Notes
The logging code is intentionally best-effort under allocation failure, falling back to direct `vfprintf`/separate error logging.
