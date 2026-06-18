# sources/test-tools/strace/src/times.c

Purpose: exit-side decoder for `times`.

Important APIs/types/functions: `SYS_FUNC(times)`, mpers `tms_t`, `umove_or_printaddr`, and `PRINT_FIELD_CLOCK_T`.

Control flow: always prints `buf`; on syscall exit, fetches `struct tms` and prints user/system CPU time for process and children.

State and persistence behavior: stateless; reads one output structure only after exit.

Dependencies and integration points: depends on `<sys/times.h>`, mpers handling, and syscall table mapping.

Risks: entry-side buffer contents are not meaningful; compat `clock_t` size must match tracee.

Test signals: successful call, bad pointer/failure, native and compat layouts, and large clock values.
