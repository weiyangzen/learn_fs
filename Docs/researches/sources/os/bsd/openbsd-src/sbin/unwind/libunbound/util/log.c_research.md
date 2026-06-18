# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/log.c

Implementation of Unbound's logging service.

Key globals:
- `verbosity`: global verbosity level, default `NO_VERBOSE`.
- `logfile`: active file sink, default unset until `log_init`.
- `logkey`: thread-local key for numeric thread ID in log output.
- `log_lock`: mutex protecting `logfile` when threads are enabled.
- `ident` / `default_ident`: process identity printed in messages.
- `logging_to_syslog`: enabled for syslog or Windows event log builds.
- `log_time_asc`, `log_time_iso`: timestamp formatting controls.

Key functions:
- `log_init(filename, use_syslog, chrootdir)`: initializes TLS key/lock, switches log destination, opens syslog or file/stderr, handles chroot path prefix stripping.
- `log_file(FILE*)`: directly sets the active file sink.
- `log_thread_set`, `log_thread_get`: store and retrieve per-thread numeric log ID.
- Identity controls: `log_ident_set`, `log_ident_set_default`, `log_ident_revert_to_default`, `log_ident_set_or_default`.
- Time controls: `log_set_time_asc`, `log_set_time_iso`.
- `log_get_lock()`: returns log lock pointer if initialized and threads are enabled.
- `log_vmsg(...)`: central formatter and sink dispatcher for syslog, Windows event log, or file logging.
- Public wrappers: `log_info`, `log_err`, `log_warn`, `fatal_exit`, `verbose`, `log_query`, `log_reply`.
- Hex/buffer logging:
  - `log_hex_f(...)` chunks binary data into uppercase hex lines.
  - `log_hex(...)` logs at current verbosity.
  - `log_buf(...)` logs an `sldns_buffer` if verbosity allows.
- Windows-only `wsa_strerror(DWORD err)`: maps many Winsock error constants to strings.

Important behavior:
- File logs include pid and thread ID.
- ISO timestamps include millisecond precision and timezone offset when supported.
- `fatal_exit` logs a critical message then exits with status 1.
- `verbose` maps verbosity levels to notice/info/debug priority classes.

Dependencies:
- Uses `util/locks.h`, `sldns/sbuffer.h`, syslog where available, Windows service event logging where applicable.

Research notes:
- Logging is process-global and lock-protected after initialization.
- `log_vmsg` truncates formatted messages to `MAXSYSLOGMSGLEN`.
