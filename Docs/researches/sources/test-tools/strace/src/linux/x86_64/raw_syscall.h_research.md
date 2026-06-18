<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/raw_syscall.h -->
# sources/test-tools/strace/src/linux/x86_64/raw_syscall.h

Purpose: provides a minimal inline raw syscall helper for x86_64.
Important APIs/types/functions: `raw_syscall_0`, `kernel_ulong_t`, inline `syscall` assembly, return in `rax`, and clobbers for `memory`, `cc`, `rcx`, `r11`.
Control flow: sets `*err` to zero, invokes syscall number with no arguments, returns raw kernel value. State and persistence behavior: no persistent state; affects CPU registers only.
Dependencies and integration points: low-level strace self-probing paths that need direct syscalls. Risks: assembly constraints must match ABI; no errno conversion is done here. Test signals: raw syscall helper tests for simple zero-argument syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/raw_syscall.h -->
