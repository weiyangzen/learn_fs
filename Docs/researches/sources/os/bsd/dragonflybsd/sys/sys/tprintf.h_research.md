# File Research: sources/os/bsd/dragonflybsd/sys/sys/tprintf.h

Kernel terminal/session printf interface.

Key contents:
- Kernel-only header.
- Defines `tpr_t` as `struct session *`.
- Forward-declares `struct proc`.
- Declares:
  - `tprintf_open(struct proc *)`
  - `tprintf_close(tpr_t)`
  - `tprintf(tpr_t, const char *, ...)`

Role:
- Provides a typed handle for printing kernel messages to a process/session-associated terminal.
- Uses printf format checking on `tprintf`.

Research notes:
- This is a narrow kernel output helper API, separate from generic `kprintf`/`log`.
