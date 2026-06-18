# File Research: sources/os/linux/linux-stable/fs/netfs/Kconfig

## Purpose

This Kconfig file defines configuration switches for the kernel netfs helper library and FS-Cache support used by network filesystems and other filesystems that want shared high-level caching and I/O helpers.

## Config Symbols

- `NETFS_SUPPORT`
  - Tristate base option for netfs helper support.
  - Enables high-level buffered I/O helpers, read segmentation, local caching integration, and transparent huge page support.
  - Other netfs objects are built under this symbol.

- `NETFS_STATS`
  - Boolean statistics gathering for local caching.
  - Depends on `NETFS_SUPPORT && PROC_FS`.
  - Exports stats through `/proc/fs/fscache/stats`.
  - The help text notes measurable overhead, especially from cacheline bouncing on multi-CPU systems.

- `NETFS_DEBUG`
  - Boolean dynamic debugging support for netfslib and FS-Cache.
  - Depends on `NETFS_SUPPORT`.
  - Allows debug output controlled through `/sys/module/netfs/parameters/debug`.

- `FSCACHE`
  - Boolean generic filesystem local caching manager.
  - Depends on `NETFS_SUPPORT`.
  - Enables pluggable local caches for network and other filesystems.
  - Points readers to `Documentation/filesystems/caching/fscache.rst`.

- `FSCACHE_STATS`
  - Boolean FS-Cache statistics.
  - Depends on `FSCACHE && PROC_FS`.
  - Selects `NETFS_STATS`.
  - Also exports through `/proc/fs/fscache/stats`.

## Dependencies And Build Impact

`FSCACHE` is layered on `NETFS_SUPPORT`; FS-Cache cannot be enabled without the netfs helper library. Stats require procfs. Debugging is independent of stats but still requires netfs support.

## Key Takeaways

The file separates core netfs infrastructure, optional debugging, optional generic local caching, and optional stats. It makes FS-Cache an extension of the netfs library rather than an independent subsystem.
