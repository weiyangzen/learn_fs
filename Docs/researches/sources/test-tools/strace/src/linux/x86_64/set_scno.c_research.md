<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/set_scno.c -->
# sources/test-tools/strace/src/linux/x86_64/set_scno.c

Purpose: rewrites the x86 syscall number register.
Important APIs/types/functions: `arch_set_scno`, `upoke`, and `ORIG_RAX` register offset.
Control flow: writes the supplied syscall number to `orig_rax` using ptrace. State and persistence behavior: mutates tracee syscall-entry state.
Dependencies and integration points: syscall tampering and injection features. Risks: x32 bit handling is the caller's responsibility; wrong offset breaks syscall rewrite. Test signals: syscall-number injection tests and x32 bit-preservation cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/set_scno.c -->
