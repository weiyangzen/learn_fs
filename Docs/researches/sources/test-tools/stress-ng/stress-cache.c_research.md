<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cache.c -->
# sources/test-tools/stress-ng/stress-cache.c

## Purpose
Implements the `cache` stressor, a CPU cache stress test that walks the shared `g_shared->mem_cache` buffer with pseudo-random read, write, and mixed write operations. It optionally injects architecture cache operations such as prefetch, cache-line flush, write-back, fences, demote, and RISC-V CBO handling to create poor locality and exercise instruction support.

## Important APIs, Types, and Functions
The public integration point is `stress_cache_info`, classified as `CLASS_CPU_CACHE`, with command options in `opts`. `CACHE_FLAGS_*` define optional cache instructions and behavior, while `mask_flag_info_t` maps flags to user-visible names. `CACHE_WRITE_USE_MOD()` generates 256 specialized `stress_cache_write_mod_0xNN()` functions, indexed by `cache_mixed_ops_funcs`, so each bitmask can be compiled as a constant. `stress_cache_read()`, `stress_cache_write()`, `stress_cache_flush()`, `stress_cache_bzero()`, and `stress_cache_permute()` cover read/write loops, invalid cacheflush probes, RISC-V zeroing, and flag-order permutation. Signal handlers use `sigsetjmp`/`siglongjmp` to recover from SIGSEGV, SIGBUS, and SIGILL.

## Control Flow
`stress_cache()` gathers options, filters unavailable instructions using compile-time feature macros and runtime CPU probes, installs signal handlers, creates an intentionally invalid address, clears the shared cache buffer, waits at the stress-ng synchronization barrier, then cycles through mixed, read, and write phases until `stress_continue()` ends. Mixed mode either uses the active flag mask or walks permutations. Each loop optionally changes CPU affinity, flushes instruction/data cache ranges, periodically probes invalid cache operations, and records metrics.

## State and Persistence Behavior
Runtime state is process-local plus shared memory in `g_shared->mem_cache`. The stressor tracks current buffer offsets, active/disabled cache flags, per-mode metrics, CPU affinity state, and signal recovery state. It does not persist files. The only intentionally invalid memory state is a mapped then unmapped page used to test fault handling.

## Dependencies and Integration Points
Depends on stress-ng core APIs for settings, metrics, bogo accounting, signals, affinity, random numbers, CPU cache information, cacheflush shims, and architecture assembly wrappers from x86 and RISC-V headers. It integrates with global shared memory prepared by stress-ng's cache infrastructure and with the common option parser through `OPT_cache_*` entries.

## Risks and Edge Cases
Architecture instructions may be compiled in but unsupported by the current CPU, so SIGILL masking is required. Invalid cacheflush probes can fault and are guarded by longjmp. Affinity changes can fail or be constrained by cpusets. Some options are no-ops on unsupported builds, and permutation counts can explode with many flags. Incorrect mask filtering could select undefined instructions or misreport metrics.

## Test Signals
Useful signals are successful startup with reported active/ignored flags, no unhandled SIGILL/SIGBUS/SIGSEGV, nonzero "cache ops per second", read, and write metrics, and optional logs showing disabled flags rather than crashes. Verification should cover plain mode, `--cache-enable-all`, `--cache-permute`, and `--cache-no-affinity` on systems with and without cache instruction support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cache.c -->
