# File Research: sources/os/linux/linux/fs/fuse/iomode.c

Manages per-inode FUSE I/O modes that prevent unsafe mixing of cached page-cache I/O, direct I/O, and passthrough backing-file I/O.

Key entry points:
- `fuse_file_io_open()` decides the mode for a newly opened FUSE file.
- `fuse_file_io_release()` drops mode references on close.
- `fuse_file_cached_io_open()` enters cached mode and waits for conflicting uncached/direct/passthrough users.
- `fuse_inode_uncached_io_start()` and `fuse_inode_uncached_io_end()` maintain negative `iocachectr` counts for uncached/passthrough mode.

Important control flow:
- Positive `fi->iocachectr` means cached users exist; negative means uncached users exist.
- Cached opens wait while `fuse_is_io_cache_wait()` is true, setting `FUSE_I_CACHE_IO_MODE` so direct writers serialize.
- Passthrough opens require `CONFIG_FUSE_PASSTHROUGH`, connection passthrough support, valid open flags, and a backing id from the open response.
- If an inode already has a backing file, later opens must also use `FOPEN_PASSTHROUGH`.

Dependencies and integration:
- Coordinates with `fuse_passthrough_open()` / `fuse_passthrough_release()`.
- Uses `fuse_inode_backing()`, `fuse_inode_backing_set()`, `fuse_backing_put()`, `fi->direct_io_waitq`, and inode state bits from `fuse_i.h`.

Risks and invariants:
- Server mistakes in open mode are converted to user-visible `-EIO`.
- `FOPEN_PARALLEL_DIRECT_WRITES` is stripped unless `FOPEN_DIRECT_IO` is present.
- First passthrough open excludes cached mode; last passthrough close wakes cached waiters and drops backing reference.
