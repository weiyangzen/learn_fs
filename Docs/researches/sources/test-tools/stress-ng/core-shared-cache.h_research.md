# sources/test-tools/stress-ng/core-shared-cache.h

Purpose: declares shared cache buffer allocation and cleanup for stressors.

Important APIs/types/functions: `stress_shared_cache_alloc(const char *name)` initializes shared cache/cacheline buffers and returns 0 or failure. `stress_shared_cache_free(void)` releases them.

Control flow: no header logic beyond inclusion guards and `WARN_UNUSED` on allocation.

State and persistence: state is held in the global shared region, not exposed through this header.

Dependencies/integration: includes `stress-ng.h` for global types/macros and is called during stress-ng shared-memory setup/teardown.

Risks: callers should treat allocation as a process-wide setup step, not a per-stressor local allocation, because the implementation writes `g_shared`.

Test signals: compile and call lifecycle around stressors that expect `g_shared->mem_cache` and `g_shared->cacheline`.
