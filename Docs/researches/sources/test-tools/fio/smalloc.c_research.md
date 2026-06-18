# sources/test-tools/fio/smalloc.c

## Purpose
`smalloc.c` implements fio's simple shared allocator backed by `mmap()`. It provides zeroed allocations that are visible across forked processes and threads, which is important for fio structures shared between the main process, job workers, and server/backend code.

## Important APIs, Types, And Functions
The public API is `sinit()`, `scleanup()`, `smalloc()`, `scalloc()`, `sfree()`, `smalloc_strdup()`, and `smalloc_debug()`. The allocator divides each pool into 32-byte blocks (`SMALLOC_BPB`) tracked by an unsigned-int bitmap. `struct pool` stores the mmap region, bitmap address, free/total counts, next non-full bitmap word, mmap size, and a semaphore lock. `struct block_hdr` stores the allocated size and, when redzones are enabled, a pre-redzone marker.

Allocation walks pools starting from `last_pool`. `smalloc_pool()` computes the allocation size including header/redzones, calls `__smalloc_pool()` to find contiguous free bitmap bits, writes the header, fills redzones, and zeroes user memory. `sfree()` finds the owning pool by range check, verifies redzones, clears bitmap bits, and updates free counters.

## Control Flow
`sinit()` maps the pool descriptor array once and then adds up to `INITIAL_POOLS` pools using `add_pool()`. `add_pool()` rounds the pool to block/bitmap boundaries, maps shared anonymous memory, places the bitmap at the end of the data area, and initializes the lock. Allocation scans bitmap words with `find_best_index()`, `find_next_zero()`, and `blocks_free()` before marking bits with `set_blocks()`. Freeing reverses the block calculation and calls `clear_blocks()`.

## State And Persistence Behavior
Allocator state is process memory mapped with `MAP_SHARED` except ESX builds use `MAP_PRIVATE`. Globals `mp`, `nr_pools`, and `last_pool` track pool descriptors and the preferred pool. `smalloc_pool_size` is externally configurable. There is no persistent on-disk state; `scleanup()` unmaps pools and descriptor storage.

## Dependencies And Integration Points
The file depends on fio semaphores, OS mmap flags, logging, and utility alignment/bit helpers. It is used by server queue entries, stats per-priority arrays, and other fio data that must survive or be visible after fork. Callers must pair `smalloc`/`scalloc` with `sfree`, not `free`, except for data explicitly allocated by libc in other modules.

## Risks And Edge Cases
`scalloc(nmemb, size)` does not check multiplication overflow. `ptr_valid()` and several allocation/free paths use `void *` arithmetic, which assumes compiler extensions. `sfree()` only logs if a pointer is not from any pool and does not abort, which can hide ownership bugs. Redzone checks assert on corruption but cannot detect all overwrites. The allocator never grows beyond `MAX_POOLS`; OOM only logs and returns NULL. `scleanup()` does not reset globals, so repeated cleanup/reinit lifecycles would be risky unless process exit follows.

## Test Signals
Tests should cover allocations around block boundaries, large allocation pool sizing, redzone corruption detection, freeing in different order, multi-pool fallback, shared visibility after fork, concurrent allocations under locks, `smalloc_strdup()` contents, and OOM behavior with small `--alloc-size`.
