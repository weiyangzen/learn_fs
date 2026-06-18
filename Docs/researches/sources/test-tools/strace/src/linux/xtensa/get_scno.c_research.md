<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_scno.c -->
# sources/test-tools/strace/src/linux/xtensa/get_scno.c

Purpose: obtains the Xtensa syscall number.
Important APIs/types/functions: `arch_get_scno`, `upeek`, `SYSCALL_NR`, and `tcp->scno`.
Control flow: peeks the syscall-number pseudo-register and returns -1 on ptrace failure or 1 on success. State and persistence behavior: updates only current `tcb` syscall number.
Dependencies and integration points: syscall dispatch. Risks: wrong `SYSCALL_NR` constant prevents table lookup. Test signals: Xtensa syscall-number extraction tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_scno.c -->
