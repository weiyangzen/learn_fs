# sources/test-tools/stress-ng/stress-malloc.c

Purpose: implements `malloc`, a memory/VM/OS stressor for allocator churn. It mixes allocation, reallocation, freeing, aligned allocation APIs, optional page touching, mlock, trimming, cache flushing, zero-on-free, pthread concurrency, and OOM handling.

Important APIs/types/functions: `stress_malloc_info_t` stores allocation pointer and length. `stress_malloc_args_t` carries per-thread status. `stress_alloc_action()` records the current allocator action for crash diagnostics. `stress_malloc_page_touch()` populates pages. `stress_malloc_loop()` performs randomized allocate/free/realloc operations. `stress_malloc_child()` installs SIGSEGV recovery and starts optional pthreads. `stress_malloc()` configures options and runs the child through `stress_oomable_child()`.

Control flow: the outer stressor sets allocation limits/options, then enters an OOMable child. The child synchronizes and runs one main allocation loop plus optional pthread loops. Each loop mmap-allocates its metadata table, randomly chooses a slot, frees or reallocates existing allocations, or creates new allocations via `calloc`, `posix_memalign`, `aligned_alloc`, `memalign`, `valloc`, or `malloc`. Verification stores the allocation address in the first word and checks it later.

State and persistence: allocator state is process heap plus an mmap metadata table. Static globals hold settings, current action, SIGSEGV jump flag, and thread-running flag. No filesystem state is created.

Dependencies/integration: requires `siglongjmp`; optionally uses pthreads, `malloc.h`, `mallopt`, `malloc_trim`, `malloc_usable_size`, mlock, cache flush, mincore, and stress-ng lock/OOM wrappers.

Risks/test signals: intentionally drives memory pressure and allocator fragmentation. Useful signals are optional pointer/usable-size verification, OOM wrapper behavior, no leaked metadata mapping, and bogo increments under mixed allocator operations.
