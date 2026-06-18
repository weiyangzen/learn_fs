# File Research: sources/teaching/os161/kern/include/kern/signal.h

Defines machine-independent signal ABI constants and structures.

Key contents:
- Signal numbers through `_NSIG`, including common Unix signals.
- `sigset_t`, `SA_*` flags, `SIG_BLOCK`/`SIG_UNBLOCK`/`SIG_SETMASK`.
- Signal handler type and magic values `SIG_DFL`, `SIG_IGN`.
- `struct sigaction` and `struct sigaltstack`.

Notable issue:
- `SIGUSR1` is defined as 20, same as `SIGCHLD`; likely inherited/teaching simplification or defect.
