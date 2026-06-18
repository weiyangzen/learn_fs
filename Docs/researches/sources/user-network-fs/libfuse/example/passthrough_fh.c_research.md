# sources/user-network-fs/libfuse/example/passthrough_fh.c

## Purpose
`passthrough_fh.c` is a more capable high-level passthrough example that stores file and directory handles in `struct fuse_file_info`. It still mirrors paths through libc syscalls, but file data operations are primarily file-descriptor based, enabling better performance, `nullpath_ok`, buffer-based reads/writes, flush/fsync, and lock support.

## Important APIs, Types, and Functions
`xmp_init()` enables `use_ino`, `nullpath_ok`, `parallel_direct_writes`, and zero cache timeouts. `struct xmp_dirp` stores a `DIR *`, current entry, and offset for stateful readdir. The operation table includes `opendir`, `readdir`, `releasedir`, `read_buf`, `write_buf`, `flush`, `fsync`, optional POSIX locks via `ulockmgr`, BSD `flock`, optional xattrs, copy-file-range, lseek, and statx.

## Control Flow
`main()` delegates to `fuse_main`. `open` and `create` store real backing file descriptors in `fi->fh`; later read/write/truncate/chmod/chown/utimens/fsync/fallocate operations use that descriptor when available. `opendir` stores an allocated `xmp_dirp` as `fi->fh`, and `readdir` uses `seekdir/telldir` offsets to support continuation. `read_buf` and `write_buf` expose FD-backed `fuse_bufvec` structures so libfuse can transfer data efficiently.

## State and Persistence
Persistent state is the backing filesystem. Runtime state consists of open backing file descriptors and allocated directory stream handles. Cache state is intentionally short-lived because entry, attr, and negative timeouts are set to zero. File locks and flock calls are forwarded to the backing file descriptors.

## Dependencies and Integration Points
This example integrates with libfuse high-level `nullpath_ok`, file-handle semantics, `fuse_buf_copy()`, platform xattr APIs, optional `libulockmgr`, `flock(2)`, `copy_file_range`, and `statx`. It uses `passthrough_helpers.h` for fallocate portability. FreeBSD directory offsets are adjusted because `telldir()` may return zero.

## Risks
The implementation remains vulnerable to path races for operations that cannot use `fi->fh`, such as unlink, rename, link creation, and xattrs. Directory handle allocation must be balanced by `releasedir`; leaks occur if abnormal teardown bypasses release. `flush` uses `close(dup(fi->fh))`, which is correct for close-like flushing but can surprise readers expecting fsync semantics. `rename` still rejects all nonzero flags.

## Test Signals
Test with common POSIX file operations while holding files open across rename/unlink to verify descriptor-based behavior. Exercise `read_buf`/`write_buf` through large reads/writes, `flock`, optional `fcntl` locks if built with `libulockmgr`, xattrs, fallocate, copy-file-range, lseek data/hole, and readdir continuation across small buffers.
