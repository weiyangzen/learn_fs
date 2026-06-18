# File Research: sources/virtualization/nbdkit/server/log-syslog.c

Purpose: Emits formatted nbdkit error messages to syslog.

Behavior:
- Uses priority `LOG_DAEMON | LOG_ERR`.
- Formats into an allocated memory stream so thread-local name/instance can be prepended.
- Restores `errno = orig_errno` before formatting for correct `%m` expansion.
- On `open_memstream` failure, falls back to `vsyslog` with the original format and arguments.
- Sends the completed message with `syslog`.

Dependencies:
- Used by `log.c` for explicit syslog logging and default logging after background fork.
