# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/errwarn.c

## Purpose
Provides common diagnostic and fatal logging routines for dhclient.

## Main Elements
- `error()`: formats message, logs to Casper syslog/stderr, removes pidfile, and exits.
- `warning()`, `note()`, `debug()`: log at error/info/debug priority and optionally stderr.
- `parse_warn()`: emits parser diagnostics with file/line, offending token line, caret location, and sets `warnings_occurred`.
- `do_percentm()`: expands `%m` in format strings using saved `errno`.

## Dependencies And Integration
Uses globals from `dhcpd.h`: `capsyslog`, `log_priority`, `log_perror`, `pidfile`, lexer state, token buffer, and source name. Called throughout parser, state machine, dispatch, and privsep code.

## Risk Notes
`error()` is process-fatal and removes the pidfile. Formatting uses static buffers, so routines are not reentrant/thread-safe, which is acceptable for this single-threaded client.
