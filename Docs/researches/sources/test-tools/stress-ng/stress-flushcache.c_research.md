# sources/test-tools/stress-ng/stress-flushcache.c

Purpose: implements `flushcache`, a CPU cache stressor that flushes or demotes data-cache lines and modifies executable code pages to force instruction-cache maintenance.

Important APIs/types/functions: `stress_flushcache_context_t` holds i-cache function pointer, data and instruction mappings, sizes, line sizes, and x86 feature flags. `clear_cache_page()`, `dcbst_page()`, `cldemote_page()`, and `clflush_page()` provide architecture-specific line operations. `stress_flush_icache()` makes the instruction mapping writable/executable, toggles bytes, calls `shim_flush_icache`, PPC `icbi`, compiler clear-cache, and `shim_cacheflush`, restores RX permissions, and executes the generated return stub. `stress_flush_dcache()` walks data pages and applies x86/PPC flushes plus `shim_cacheflush`.

Control flow: `stress_flushcache()` discovers LLC/data and L1 instruction cache sizes, applies user byte overrides, clamps to page size, accounts for NUMA node scaling, maps an executable instruction-cache page, copies `stress_ret_opcode` into it, and runs `stress_flushcache_child()` through the OOM-child wrapper. The child maps the data buffer, disables huge pages where possible, synchronizes, and loops over instruction and data flushes until stopped.

State and persistence behavior: all state is anonymous memory. The instruction mapping is shared and executable; the data mapping is shared in the child and unmapped on exit. No files are created.

Dependencies and integration points: build requires supported architectures, `mprotect()`, compiler support, and architecture cacheflush/return-stub support. Integrates with core arch asm helpers, cache-size discovery, NUMA helpers, mmap/OOM wrappers, and the stressor `supported` hook `stress_asm_ret_supported`. Registered as `CLASS_CPU_CACHE`.

Risks: executable writable mappings and cache instructions are architecture-sensitive and can fail under W^X policies, seccomp, or unusual kernels. Help text has misspelled option labels `flushcashe-*` while opts use `flushcache-*`. The instruction flush loop uses data cache line size for stepping through i-cache bytes, which is probably intentional fallback but should be reviewed on split-line-size architectures.

Test signals: build/run on x86, ARM, RISC-V, s390, PPC/PPC64 where supported. Verify skip behavior when executable mmap or mprotect fails, perf cache-miss counters move, NUMA scaling message appears on multi-node systems, and both user byte options are honored.
