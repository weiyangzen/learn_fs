<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cachehammer.c -->
# sources/test-tools/stress-ng/stress-cachehammer.c

## Purpose
Implements the `cachehammer` stressor, which repeatedly applies cache and memory access primitives to pairs of addresses across shared cache memory, local anonymous mappings, a shared file-backed page, and intentionally invalid pages. It is designed to hammer cache coherency, prefetch, flush, write-back, architecture-specific cache instructions, and optional NUMA page movement.

## Important APIs, Types, and Functions
`stress_cachehammer_info` exposes the stressor with `init`, `deinit`, options, and per-method metrics. `stress_cachehammer_context_t` holds active buffers, page masks, method index, valid/trapped method bitsets, NUMA masks, and runtime flags. `stress_cachehammer_func_t` describes each hammer method with a name, permutation eligibility, validity predicate, and `hammer_func_t`. Methods include generic read/write/read-write variants, `clearcache`, x86 `clflush`, `clflushopt`, `clwb`, `cldemote`, prefetch variants, RISC-V `cbo_zero`, and PowerPC cache block operations when available.

## Control Flow
`stress_cachehammer_init()` creates a temporary directory and file containing one page for shared file-backed mappings; `deinit` removes it. `stress_cachehammer()` builds the valid method mask, optionally reduces it to permutation-capable operations, maps a local buffer, local page, bad page, and file page, installs signal handlers, then runs either random method selection or flag permutation. `stress_cachehammer_exercise()` chooses one of several address classes and invokes the active hammer method, updating per-method timing. Faulting methods are recorded in `ctxt.trapped` and skipped on later iterations.

## State and Persistence Behavior
The stressor creates a temporary `cachehammer` directory and `mmap-page` file for the lifetime of the run, then removes them in `deinit`. It keeps a global context because signal handlers need to mark the currently executing method. Memory state spans `g_shared->mem_cache.buffer`, anonymous local mappings, a shared file mapping, and optional NUMA masks. Metrics are stored per hammer method.

## Dependencies and Integration Points
Uses stress-ng core helpers for temp files, shared cache memory, random numbers, metrics, settings, signal handling, NUMA, and architecture feature checks. It depends on architecture assembly wrappers in generic, x86, RISC-V, and PowerPC headers, plus `msync`, `mmap`, and optional Linux memory policy support. Options are `cachehammer-method` and `cachehammer-numa`.

## Risks and Edge Cases
The method table can have more entries than a 32-bit mask can safely represent if extended without widening bitsets. Some valid predicates rely on runtime CPU probes; wrong probes can trigger SIGILL and method trapping. Temporary file setup failure skips the stressor. NUMA randomization must tolerate unavailable policy APIs or node masks. Bad-page probes intentionally risk faults, so signal recovery must stay correct.

## Test Signals
Expected evidence includes log output listing the selected method and available operations, nonzero per-operation `cache bogo-ops/sec` metrics, clean cleanup of the temporary file and directory, and disabled-operation logs after trapped signals rather than process termination. Exercise both `--cachehammer-method random` and `permute`, with and without `--cachehammer-numa`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cachehammer.c -->
