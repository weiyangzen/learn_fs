# File Research: sources/virtualization/nbdkit/plugins/file/file.c

POSIX implementation of the production nbdkit file plugin.

Supported modes:
- `file=<FILENAME>` / magic file parameter.
- `dir=<DIRNAME>` or `directory=<DIRNAME>`, exposing each regular/block file as an export.
- `fd=<FD>`, serving an inherited regular/block file descriptor.
- `dirfd=<FD>`, serving files under an inherited directory descriptor.
- Optional `fadvise=normal|random|sequential`.
- Optional `reduce-memory-pressure=true`.
- Backward-compatible `cache=default|none`.

Config/lifecycle:
- Ensures exactly one source mode is configured.
- Validates regular files, block devices, or directories at config completion.
- In directory modes, lists exports by scanning regular and block-device entries.
- Rejects export names containing `/`.
- Opens a per-connection fd and gathers stat/block-device information.
- Duplicates inherited fds for connection-local use.

Capabilities:
- Parallel thread model.
- Multi-connection capable.
- Write capability depends on readonly mode and actual fd access mode.
- Native FUA via `fdatasync`.
- Trim support when hole punching is compiled in.
- Optional extents support via `SEEK_DATA`/`SEEK_HOLE`.
- Optional cache support via `posix_fadvise(POSIX_FADV_WILLNEED)`.
- Reports rotational and block-size information for Linux block devices when ioctls are available.

I/O behavior:
- `pread` and `pwrite` loop until the full request is transferred.
- `pwrite` honors FUA by flushing.
- `flush` calls `fdatasync`.
- `zero` tries optimized methods in order: hole punching, block discard plus zero range, zero range, punch-plus-fallocate, `BLKZEROOUT`, then falls back by returning `EOPNOTSUPP`.
- `trim` tries hole punching, then block discard, and otherwise succeeds as advisory no-op.
- `extents` maps filesystem holes to `NBDKIT_EXTENT_HOLE|NBDKIT_EXTENT_ZERO`.

Memory pressure mode:
- Reads can evict pages with `POSIX_FADV_DONTNEED`.
- On Linux, writes are queued in windows, asynchronously synced, then older windows are evicted with `sync_file_range` and `posix_fadvise`.

Concurrency details:
- `lseek` users are serialized with `lseek_lock`.
- Write-eviction tracking uses mutex/rwlock protection so close cannot invalidate fds while eviction is using them.
