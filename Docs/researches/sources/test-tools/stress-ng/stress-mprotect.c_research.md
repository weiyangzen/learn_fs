# sources/test-tools/stress-ng/stress-mprotect.c

Purpose: implements `mprotect`, a VM/OS stressor that changes protection masks over shared pages from multiple processes and verifies that disallowed reads/writes fault rather than silently succeeding.

Important APIs/types/functions: `stress_mprotect_flags_t` names protection bits for diagnostics. `stress_flag_permutation()` generates all protection flag combinations from available `PROT_*` bits except exec. `stress_mprotect_mem()` installs SIGSEGV/SIGBUS handlers, randomly chooses pages/ranges, calls `mprotect()`, then probes read/write behavior. `stress_mprotect()` allocates shared memory, forks worker children, synchronizes them, and reaps them.

Control flow: the parent allocates a shared PID array and a small shared mapping, marks it mergeable, enables OOM killability, then forks up to seven child workers. Parent and children wait on stress-ng synchronization and run `stress_mprotect_mem()` concurrently against the same shared mapping. The loop randomly selects ranges at least one page long, tries up to ten protection combinations, increments bogo on successful changes, and uses signal recovery for expected protection faults. Parent kills/waits children and frees shared resources.

State and persistence: state is the shared mapping, generated protection flag array, and shared PID list. No filesystem state exists. Signal jump buffer is static per process.

Dependencies and integration: gated by `HAVE_MPROTECT`; uses stress-ng sync PID helpers, kill helpers, madvise mergeable, OOM adjustment, flag permutation, signal helpers, and optional `PROT_SEM`, `PROT_SAO`, growth flags.

Risks and test signals: concurrent protection changes can create timing-dependent faults, and some protection flags are platform-specific. Test signals are bogo increments, absence of unexpected readable/writable pages under disallowed flags, correct child cleanup, and unimplemented status without `mprotect()`.
