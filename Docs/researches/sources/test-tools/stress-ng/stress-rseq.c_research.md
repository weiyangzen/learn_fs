# sources/test-tools/stress-ng/stress-rseq.c

Purpose: implements `rseq`, a Linux restartable-sequences stressor that repeatedly enters an intentionally long critical section and measures interruptions/aborts.

Important APIs/types/functions: `rseq_info_t` stores critical-section counts, interruption counts, and SIGSEGV count. `stress_rseq_get_area()` derives libc's rseq area from `__builtin_thread_pointer()` plus `__rseq_offset`. `rseq_test()` creates a `struct rseq_cs`, registers it in `rseq_area->rseq_cs`, checks CPU consistency, stalls, and records aborts. `stress_rseq_supported()` validates libc/kernel rseq availability.

Control flow: `stress_rseq()` maps shared stats, finds the rseq area, synchronizes, and runs `stress_rseq_oomable()` through the OOM wrapper. The child installs a SIGSEGV handler and loops 10,000 critical-section attempts per bogo operation, using `cpu_id_start` as the expected CPU. On exit the parent reports interruptions per billion rseq ops.

State and persistence: shared anonymous `rseq_info` preserves counts across OOM/SEGV child behavior; `rseq_area` is thread-local libc state. No filesystem state exists.

Dependencies and integration points: requires Linux rseq headers, `__NR_rseq`, `__rseq_offset`, syscall support, GCC/musl compiler support, built-in thread pointer, assembly NOP, and excludes clang/ICC/ICX. It uses stress-ng OOM child handling, mmap, metrics, and support probing.

Risks and test signals: rseq ABI layout and compiler label-address assumptions are fragile, so unsupported toolchains are excluded. Signals include support-skip messages for unreadable/disabled rseq area, interruption-rate metric, and no unexpected SIGSEGV escalation.
