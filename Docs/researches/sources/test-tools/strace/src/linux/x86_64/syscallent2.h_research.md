<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent2.h -->
# sources/test-tools/strace/src/linux/x86_64/syscallent2.h

Purpose: x86_64 personality 2 syscall table shim for x32 tracees.
Important APIs/types/functions: includes `../x32/syscallent.h`.
Control flow: no executable logic. State and persistence behavior: static include alias.
Dependencies and integration points: selected when `__X32_SYSCALL_BIT` identifies x32. Risks: x32 table drift causes wrong compat decoding. Test signals: x32 syscall smoke tests and mixed-personality exec tracing.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent2.h -->
