# sources/test-tools/stress-ng/core-cpu-cache.h

Purpose: cache data model, cache query API, cache flush shim, prefetch shim, and memory-fence shim declarations.

Important APIs and control flow: defines `stress_cpu_cache_type_t`, `stress_cpu_cache_t`, per-CPU and CPU-list structures, query/free/flush prototypes, `SHIM_ICACHE/DCACHE`, lazy x86 `shim_clflush`, prefetch fallback, and `shim_mfence` selecting OR1K/RISC-V/x86/PPC64/SPARC or `__sync_synchronize`.

State and persistence: static `shim_clflush_func` lazily switches from selector to real/no-op function in each translation unit including the header.

Dependencies and integration: pulls in architecture assembly headers and `core-cpu.h`; widely used by memory/cache stressors.

Risks and test signals: header-level static function pointer means per-translation-unit lazy state; fence selection depends on include-time macros. Signals are compile coverage and stressors observing expected cache/fence behavior.
