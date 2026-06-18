# File Research: sources/os/linux/linux-stable/fs/netfs/Makefile

## Purpose

This Makefile defines the object composition for the `netfs` kernel module/built-in object under `CONFIG_NETFS_SUPPORT`.

## Core Objects

`netfs-y` includes the core helper library:

- Buffered I/O:
  - `buffered_read.o`
  - `buffered_write.o`
- Direct/unbuffered I/O:
  - `direct_read.o`
  - `direct_write.o`
- Iterator and locking helpers:
  - `iterator.o`
  - `locking.o`
- Common infrastructure:
  - `main.o`
  - `misc.o`
  - `objects.o`
- Read pipeline:
  - `read_collect.o`
  - `read_pgpriv2.o`
  - `read_retry.o`
  - `read_single.o`
  - `rolling_buffer.o`
- Write pipeline:
  - `write_collect.o`
  - `write_issue.o`
  - `write_retry.o`

## Conditional Objects

- `CONFIG_NETFS_STATS`
  - Adds `stats.o`.

- `CONFIG_FSCACHE`
  - Adds FS-Cache implementation pieces:
    - `fscache_cache.o`
    - `fscache_cookie.o`
    - `fscache_io.o`
    - `fscache_main.o`
    - `fscache_volume.o`

- `CONFIG_PROC_FS && CONFIG_FSCACHE`
  - Adds `fscache_proc.o`.

- `CONFIG_FSCACHE_STATS`
  - Adds `fscache_stats.o`.

## Output

`obj-$(CONFIG_NETFS_SUPPORT) += netfs.o` builds the aggregate netfs object when support is enabled.

## Key Takeaways

The Makefile shows the netfs library as a single aggregate object with optional stats and FS-Cache pieces. The read/write code is split into high-level buffered/direct entry points and lower-level collection/issue/retry machinery.
