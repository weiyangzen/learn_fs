# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/subr.c

Common logging and error helpers for fax tools.

Key behavior:
- `verbose()` writes syslog messages when `vflag` is set.
- `error()` prints a formatted fatal message to stderr, optionally echoes to stdout, and exits.
- `seterror()` writes a user-facing retry/system/protocol error string into `m->error`.
- `faxrlog()` logs receive status, timestamp, success flag, page count, and optional FTSI.

Important implementation details:
- Error strings intentionally include `Retry, ...` for queue integration.
- `Esys` includes `%r` in the stored modem error.

Risks and invariants:
- `faxxlog()` is declared in `modem.h` but not implemented in this file.
