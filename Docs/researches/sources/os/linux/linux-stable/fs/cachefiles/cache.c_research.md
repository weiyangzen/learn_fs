# File Research: sources/os/linux/linux-stable/fs/cachefiles/cache.c

This file manages high-level CacheFiles cache registration, space accounting, culling thresholds, withdrawal, and backing filesystem sync.

Primary functions:
- `cachefiles_add_cache()`: brings a cache online. It acquires an FS-Cache cache cookie, establishes security credentials, resolves the configured root directory, rejects idmapped and read-only mounts, validates required backing filesystem operations, reads statfs data, computes file/block culling thresholds, creates or opens `cache` and `graveyard` directories, registers with FS-Cache, and marks the cache ready.
- `cachefiles_has_space()`: checks free files and blocks against configured stop/cull/run thresholds. It subtracts pending write reservations from available blocks, starts culling when below cull thresholds, stops allocation below stop thresholds, and clears culling when above run thresholds.
- `cachefiles_withdraw_cache()`: unregisters from FS-Cache, withdraws fscache volumes and active objects, waits for object cleanup, withdraws CacheFiles volumes, syncs the backing filesystem, and relinquishes the cache cookie.
- Internal helpers withdraw active objects, withdraw fscache volumes, withdraw cachefiles volume structures, and sync the backing superblock.

Key constraints enforced:
- Backing root must support lookup, mkdir, tmpfile, xattrs, statfs, sync_fs, and a block size no larger than `PAGE_SIZE`.
- Idmapped mounts are rejected.
- The cache root must not be read-only.
- Cache limits are computed as percentages of total file and block counts at bind time.

Integration points:
- Calls into `security.c` for credential setup.
- Calls into `namei.c` for creating/opening cache directories.
- Registers `cachefiles_cache_ops` from `interface.c` with FS-Cache.
- Signals daemon state changes when culling starts or stops.

Error handling:
- VFS and statfs errors are traced.
- `-EIO` from backing operations marks the cache dead through `cachefiles_io_error()`.
- Partial setup is unwound by releasing directories, mount references, credentials, and FS-Cache cache cookies.
