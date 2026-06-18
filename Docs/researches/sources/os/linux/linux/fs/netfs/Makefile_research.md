# File Research: sources/os/linux/linux/fs/netfs/Makefile

## Role

Build rules for the Linux netfs helper module/object.

## Object Composition

`netfs-y` always includes:

- `buffered_read.o`
- `buffered_write.o`
- `direct_read.o`
- `direct_write.o`
- `iterator.o`
- `locking.o`
- `main.o`
- `misc.o`
- `objects.o`
- `read_collect.o`
- `read_pgpriv2.o`
- `read_retry.o`
- `read_single.o`
- `rolling_buffer.o`
- `write_collect.o`
- `write_issue.o`
- `write_retry.o`

Conditional objects:

- `stats.o` when `CONFIG_NETFS_STATS` is enabled.
- FS-Cache core objects when `CONFIG_FSCACHE` is enabled:
  - `fscache_cache.o`
  - `fscache_cookie.o`
  - `fscache_io.o`
  - `fscache_main.o`
  - `fscache_volume.o`
- `fscache_proc.o` when both `CONFIG_FSCACHE` and `CONFIG_PROC_FS=y`.
- `fscache_stats.o` when `CONFIG_FSCACHE_STATS` is enabled.

Final target:

- `obj-$(CONFIG_NETFS_SUPPORT) += netfs.o`

## Research Notes

The Makefile shows netfs as one composite object built from shared read/write, iterator, request/object, and retry/collector code. FS-Cache is compiled into the same `netfs.o` composite only when local caching is configured.
