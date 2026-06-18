<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_regs.h -->
# sources/test-tools/strace/src/linux/x86_64/arch_regs.h

Purpose: supplies numeric x86_64 register indexes for `upoke`/`upeek` operations.
Important APIs/types/functions: constants `R15` through `GS`, including `RAX`, `ORIG_RAX`, `RIP`, and `RSP`.
Control flow: no executable logic. State and persistence behavior: compile-time constants only.
Dependencies and integration points: used by `set_error.c`, `set_scno.c`, and register tampering paths. Risks: indexes are byte-scaled by callers, so a wrong ordinal writes the wrong tracee register. Test signals: syscall injection and syscall-number rewrite tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_regs.h -->
