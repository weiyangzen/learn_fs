# File Research: sources/os/bsd/netbsd-src/sys/sys/tprintf.h

Read completely: 44 lines.

Declares terminal-associated kernel printf helpers.

Key elements:
- `tpr_t` is an opaque `struct session *` handle.
- `tprintf_open(struct proc *)` opens a terminal print context for a process.
- `tprintf_close(tpr_t)` releases it.
- `tprintf(tpr_t, const char *, ...)` formats output to the associated terminal.

Risks and notes:
- Intended for kernel messages associated with a session/controlling terminal.
- Format string checking is enabled through `__printflike`.
