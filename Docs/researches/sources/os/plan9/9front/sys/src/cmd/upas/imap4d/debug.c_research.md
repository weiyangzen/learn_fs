# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/debug.c

This file centralizes IMAP daemon logging.

Key behavior:
- Defines `logfile` as `imap4d`.
- `debuglog` logs only when global `debug` is nonzero.
- `ilog` logs unconditionally.
- Both include username and process id in syslog messages.

Integration and risks:
- Depends on global `username` and `debug` from the daemon.
