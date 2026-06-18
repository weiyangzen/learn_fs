# sources/test-tools/strace/src/sysinfo.c

Purpose: exit-side decoder for `sysinfo`.

Important APIs/types/functions: `SYS_FUNC(sysinfo)`, mpers `sysinfo_t`, `umove_or_printaddr`, and field printers for uptime, loads, memory totals, swap totals, process count, high memory, and memory unit.

Control flow: entry returns 0 without printing. On exit, prints `info`, fetches the tracee structure if possible, and emits all relevant fields.

State and persistence behavior: no persistent state; reads one output structure after syscall completion.

Dependencies and integration points: depends on `<sys/sysinfo.h>`, mpers layout handling, and array member printer helpers.

Risks: printing on entry would expose uninitialized output buffers, so exit-only behavior is important. Compat layout must match tracee personality.

Test signals: successful call, failed call/bad pointer, native and compat mpers, and non-default memory-unit values.
