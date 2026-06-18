# sources/user-network-fs/libfuse/example/passthrough.c

## Purpose
`passthrough.c` is the simplest high-level FUSE passthrough example. It mirrors the host filesystem namespace visible from the process root by forwarding operations to libc/path-based syscalls. The comments explicitly note that performance is poor; the value is demonstrating high-level API callback coverage.

## Important APIs, Types, and Functions
`xmp_oper` registers high-level callbacks for attributes, access, readlink, directory listing, creation/removal, rename/link, chmod/chown/truncate, utimens, open/create, read/write, statfs, release, fsync, fallocate, xattrs, copy_file_range, lseek, and statx when available. `xmp_init()` configures `use_ino`, `parallel_direct_writes`, and cache timeouts. `passthrough_helpers.h` supplies `mknod_wrapper()` and `do_fallocate()`.

## Control Flow
`main()` sets `umask(0)`, strips two example-specific options (`--plus` and `--readdir-zero-inodes`) into globals, and delegates to `fuse_main`. Each callback maps the FUSE path directly to a libc operation: `lstat`, `access`, `opendir/readdir`, `mknod_wrapper`, `mkdir`, `unlink`, `rename`, `open`, `pread`, `pwrite`, and so on. For reads, writes, fallocate, copy, and lseek, the code uses `fi->fh` if available and opens by path only when libfuse calls statelessly.

## State and Persistence
The filesystem persists by modifying the underlying filesystem directly; no separate metadata database exists. Runtime state is limited to `fill_dir_plus`, `readdir_zero_ino`, and file descriptors stored in `fi->fh`. `xmp_init()` disables entry/attribute/negative cache timeouts unless `auto_cache` is set, reducing stale hardlink metadata.

## Dependencies and Integration Points
The code depends on high-level libfuse and platform feature macros for `utimensat`, xattrs, `copy_file_range`, and `statx`. It integrates with kernel caching through `struct fuse_config`, with directory cache prefill through `FUSE_FILL_DIR_PLUS`, and with direct I/O write concurrency by setting `parallel_direct_writes` when direct I/O is active.

## Risks
Because operations are path-based, races between lookup and operation are expected, especially around rename/unlink and symlinks. The filesystem starts at process `/`, so mounting it exposes the daemon's whole namespace subject to permissions. `MAX_ARGS` silently caps processed arguments at ten. `xmp_readdir()` ignores `fstatat` errors in plus mode and may report partial attributes. It implements `rename` flags only by rejecting any nonzero flags.

## Test Signals
Smoke tests should mount in a temporary directory and compare common operations against the backing root: create/read/write/truncate/link/rename/unlink, xattr when built, `copy_file_range`, sparse-file `lseek`, and `statx`. `--plus` should trigger attribute-prefilled readdir, while `--readdir-zero-inodes` should report zero inode numbers from directory entries.
