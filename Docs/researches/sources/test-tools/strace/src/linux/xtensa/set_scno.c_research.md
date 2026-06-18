<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/set_scno.c -->
# sources/test-tools/strace/src/linux/xtensa/set_scno.c

Purpose: rewrites the Xtensa syscall-number pseudo-register.
Important APIs/types/functions: `arch_set_scno`, `upoke`, and `SYSCALL_NR`.
Control flow: pokes the supplied syscall number into the tracee. State and persistence behavior: mutates tracee syscall-entry state.
Dependencies and integration points: syscall injection/tampering. Risks: wrong pseudo-register constant breaks rewrite. Test signals: Xtensa syscall-number tampering tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/set_scno.c -->
