# sources/test-tools/strace/src/sysctl.c

Purpose: decoder for obsolete `_sysctl`.

Important APIs/types/functions: `SYS_FUNC(sysctl)`, mpers type declaration for `struct_sysctl_args`, `umove_or_printaddr`, and field printers for pointers, signed length, and unsigned new length.

Control flow: prints the argument pointer name, fetches the tracee `__sysctl_args` structure, and emits `name`, `nlen`, `oldval`, `oldlenp`, `newval`, and `newlen`.

State and persistence behavior: stateless; reads one tracee structure.

Dependencies and integration points: depends on Linux `sysctl.h`, mpers layout handling, and syscall table entry for old sysctl.

Risks: only prints pointer fields, not nested name arrays or values. Correctness depends on mpers structure layout for compat tracees.

Test signals: NULL/bad pointer, native and compat layouts, read-only sysctl with `oldval`, write sysctl with `newval`, and unusual lengths.
