# sources/test-tools/stress-ng/stress-mseal.c

Purpose: implements `mseal`, a VM/OS stressor for Linux memory sealing. It verifies that sealed mappings reject operations that would alter, unmap, or replace them, while repeated sealing of mapped ranges succeeds.

Important APIs/types/functions: global `mapping`, `mapping_size`, and `no_mapping` provide the sealed range and an unmapped address range. `stress_mseal_supported()` probes `shim_mseal()` support before registration. Expectation helpers compare return values and errno. `mseal_funcs[]` dispatches negative tests for `madvise(MADV_DONTNEED)`, `mremap` resize/move, `munmap`, `mprotect`, fixed `mmap`, sealing unmapped pages, and positive tests for sealing first, last, and all mapped pages.

Control flow: support probing maps two pages read-only and seals them. Runtime ensures a mapping exists, creates and unmaps another two-page range to use as a known hole, synchronizes, then repeatedly runs all test functions. Positive `mseal()` calls are timed and counted; any unexpected result stops the loop. Deinit reports calls/sec and attempts to unmap the sealed mapping, ignoring the expected failure.

State and persistence: static globals persist during the stressor instance. Sealed memory may intentionally resist cleanup until process exit. No filesystem state is created.

Dependencies and integration: uses `core-shim` for `shim_mseal`, mmap helpers, optional madvise/mremap/mprotect/fixed mmap support, stress-ng supported callback, metrics, and synchronization.

Risks and test signals: the syscall is kernel-version dependent and has strict errno expectations. If the semantics change, tests may fail despite system correctness. Signals are support skip on `ENOSYS`, EPERM/ENOMEM matches for protected operations, successful repeated sealing of mapped pages, and nonzero mseal rate metrics.
