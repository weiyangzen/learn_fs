# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_pool.c

Purpose: Implements per-mount CHFS pool allocator wrappers and a small-size string pool backed by NetBSD pools.

Key entry points:
- `chfs_pool_init`, `chfs_pool_destroy`: initialize/destroy a `struct chfs_pool`.
- `chfs_pool_page_alloc`, `chfs_pool_page_free`: custom pool allocator hooks that account against `chm_pages_used`.
- `chfs_str_pool_init`, `chfs_str_pool_destroy`: initialize/destroy 16 through 1024 byte string pools.
- `chfs_str_pool_get`, `chfs_str_pool_put`: bucket strings by requested length.

Important behavior:
- Pool names include the object purpose and mount pointer.
- Page allocation refuses allocations once `chm_pages_used` reaches `CHFS_PAGES_MAX(chmp)`.
- String buckets are fixed at 16, 32, 64, 128, 256, 512, and 1024 bytes.

Dependencies:
- NetBSD `pool`, `pool_allocator`, and atomics.
- `CHFS_POOL_GET/PUT` are declared in `chfs_pool.h`.

Research notes:
- `chfs_pool_page_alloc` calls `pool_get(pp, flags | PR_WAITOK)` from inside a pool allocator hook, which is unusual and depends on local allocator assumptions.
- String-pool calls assert `len <= 1024`.
