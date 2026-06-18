# File Research: sources/virtualization/nbdkit/plugins/split/split.c

Implements a plugin that concatenates multiple local files/devices into one exported block device. Configuration appends `file=` paths after resolving them to real paths; each connection opens all files read-only or read-write, records their offsets and sizes, and computes total size.

I/O maps global offsets to component files with `bsearch` over the offset table, then loops across file boundaries for reads and writes. It can expose extents using `SEEK_DATA`/`SEEK_HOLE` with a global lseek mutex, falling back to allocated extents when a component lacks support; cache support is optionally implemented with `posix_fadvise`.

The plugin uses `NBDKIT_THREAD_MODEL_SERIALIZE_REQUESTS` and preserves errno. Notable implementation risks visible in this file: `split_pwrite` and `split_cache` pass the global offset to `pwrite`/`posix_fadvise` where the per-file offset appears intended, and `split_cache` subtracts the zero success return from `count`, which would not advance the loop on successful `posix_fadvise`.
