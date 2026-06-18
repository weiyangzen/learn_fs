# File Research: sources/os/linux/linux/fs/netfs/Kconfig

## Role

Kconfig definitions for Linux netfs helper library and FS-Cache support.

## Options

- `NETFS_SUPPORT`
  - Tristate base option enabling network filesystem helpers.
  - Described as providing high-level buffered I/O helpers, read segmentation, local caching abstraction, and transparent huge page support.
- `NETFS_STATS`
  - Boolean statistics gathering option.
  - Depends on `NETFS_SUPPORT && PROC_FS`.
  - Exports local caching statistics through `/proc/fs/fscache/stats`.
  - Help text notes debugging value and possible multi-CPU cacheline overhead.
- `NETFS_DEBUG`
  - Boolean dynamic debugging option.
  - Depends on `NETFS_SUPPORT`.
  - Enables debug output controlled through `/sys/module/netfs/parameters/debug`.
- `FSCACHE`
  - Boolean general filesystem local caching manager.
  - Depends on `NETFS_SUPPORT`.
  - Enables pluggable local cache backends for network and other filesystems.
  - Points to `Documentation/filesystems/caching/fscache.rst`.
- `FSCACHE_STATS`
  - Boolean FS-Cache statistics option.
  - Depends on `FSCACHE && PROC_FS`.
  - Selects `NETFS_STATS`.
  - Exports the same `/proc/fs/fscache/stats` interface and references FS-Cache documentation.

## Dependencies

Defines feature switches consumed by `fs/netfs/Makefile` and by conditional compilation throughout the netfs and FS-Cache implementation.

## Research Notes

The configuration hierarchy makes `NETFS_SUPPORT` the base library switch and layers FS-Cache plus statistics/debug facilities on top. FS-Cache statistics automatically select netfs statistics so cache-level counters share the common reporting path.
