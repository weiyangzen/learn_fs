<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_syscall_number.c -->
# sources/test-tools/strace/src/print_syscall_number.c

Purpose: prints syscall numbers as fixed-width output attributes.

Important APIs/types/functions: `print_syscall_number` and `tcp->true_scno`.

Control flow: emits an attribute containing the true syscall number when known, otherwise prints unavailable marker, then emits a trailing space.

State and persistence behavior: reads per-tcb syscall state only.

Dependencies and integration points: used by output prefix logic when syscall number display is enabled.

Risks: `true_scno == -1` must be treated as unavailable rather than a huge unsigned value.

Test signals: known syscall number, unavailable syscall number, and output prefix alignment.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_syscall_number.c -->
