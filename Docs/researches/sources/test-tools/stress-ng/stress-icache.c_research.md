# sources/test-tools/stress-ng/stress-icache.c

## Purpose
`stress-icache.c` stresses instruction-cache behavior by creating executable anonymous pages filled with return opcodes, repeatedly modifying cache-line-sized chunks of the executable code, flushing instruction caches, restoring execute permissions, and calling the generated functions.

## Important APIs, Types, And Functions
The option `icache-pages` controls the number of pages. `icache_madvise_nohugepage()` requests `MADV_NOHUGEPAGE` where available. `icache_mprotect()` wraps protection changes. `stress_icache_func()` performs the modify/flush/execute loop. `stress_icache()` allocates executable memory with `stress_mmap_populate()`, copies `stress_ret_opcode.opcodes` every 64 bytes, synchronizes workers, runs the loop, and unmaps pages. `stress_icache_info` uses `stress_asm_ret_supported` as the supported hook.

## Control Flow
After size selection and SIGSEGV catching, the stressor mmaps RWX pages, names the mapping, populates return stubs, reports memory use, waits at the barrier, and calls `stress_icache_func()`. The loop toggles page protections to RWX, bit-flips/restores words every 64 bytes with `shim_flush_icache()`, changes pages back to RX, calls each return stub, flushes cache, and increments bogo ops.

## State And Persistence
State is the anonymous executable mapping and local counters. No files are written. The stressor temporarily creates writable executable pages.

## Dependencies And Integration Points
It is gated to selected architectures with `HAVE_MPROTECT`, return-opcode support, cache flush shims, mmap helpers, signal handling, and stress-ng settings/metrics.

## Risks
W^X policies, SELinux, hardened kernels, or architecture restrictions can reject RWX mappings or protection changes. Self-modifying code can fault if cache flush semantics are wrong. Huge pages would undermine the intended page behavior, hence `MADV_NOHUGEPAGE`.

## Test Signals
Signals include supported-hook pass/fail, graceful skip on `mmap` or `mprotect` denial, no SIGSEGV during generated calls, correct page-count scaling, and observable instruction-cache misses under perf.
