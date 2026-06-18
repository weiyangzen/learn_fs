<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/shuffle_scno.c -->
# sources/test-tools/strace/src/linux/x86_64/shuffle_scno.c

Purpose: normalizes x86 syscall numbers for table lookup across x86_64, i386, and x32 personalities.
Important APIs/types/functions: `shuffle_scno`, `tcp->scno`, current personality, and `__X32_SYSCALL_BIT`.
Control flow: strips or adjusts architecture-specific syscall-number bits/offsets after personality has been selected. State and persistence behavior: modifies only the current `tcb` syscall number.
Dependencies and integration points: dispatch table indexing before decoder lookup. Risks: off-by-one or missing x32-bit handling selects the wrong `sysent` row. Test signals: table-index tests for x32 high-bit syscalls and normal x86_64 numbers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/shuffle_scno.c -->
