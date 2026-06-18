# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_pool.h

Purpose: Declares CHFS pool wrapper structures and APIs.

Key definitions:
- `struct chfs_pool`: embeds a NetBSD `struct pool`, the owning `chfs_mount`, and a name buffer.
- `struct chfs_str_pool`: grouped pools for fixed-size string allocations from 16 to 1024 bytes.
- `CHFS_POOL_GET`, `CHFS_POOL_PUT`: convenience casts to NetBSD `pool_get`/`pool_put`.

Declared APIs:
- `chfs_pool_init`, `chfs_pool_destroy`.
- `chfs_str_pool_init`, `chfs_str_pool_destroy`.
- `chfs_str_pool_get`, `chfs_str_pool_put`.

Dependencies:
- Kernel-only API declarations; implementation is in `chfs_pool.c`.
- Requires `struct chfs_mount` from broader CHFS headers.

Research notes:
- The wrapper’s first field is `struct pool`, enabling cast-based use by `CHFS_POOL_GET/PUT`.
