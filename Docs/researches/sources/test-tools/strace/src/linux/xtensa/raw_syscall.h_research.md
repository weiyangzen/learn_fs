<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/raw_syscall.h -->
# sources/test-tools/strace/src/linux/xtensa/raw_syscall.h

Purpose: provides Xtensa inline raw zero-argument syscall helper.
Important APIs/types/functions: `raw_syscall_0`, `kernel_ulong_t`, register variable bound to `a2`, and `syscall` assembly.
Control flow: places the syscall number in `a2`, executes `syscall`, returns `a2`, and leaves errno conversion to callers. State and persistence behavior: no persistent state.
Dependencies and integration points: direct syscall probing in strace runtime. Risks: Xtensa calling convention constraints must remain exact. Test signals: helper smoke tests for a simple zero-argument syscall.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/raw_syscall.h -->
