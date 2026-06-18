# File Research: sources/os/linux/linux/fs/fuse/passthrough.c

Implements FUSE passthrough operations that forward reads, writes, splice, and mmap to a kernel backing file while preserving FUSE-visible inode metadata effects.

Key entry points:
- `fuse_passthrough_read_iter()`, `fuse_passthrough_write_iter()`
- `fuse_passthrough_splice_read()`, `fuse_passthrough_splice_write()`
- `fuse_passthrough_mmap()`
- `fuse_passthrough_open()` and `fuse_passthrough_release()`

Important control flow:
- Read/splice-read/mmap use a `backing_file_ctx` with `ff->cred` and an accessed callback that invalidates FUSE atime.
- Write/splice-write lock the FUSE inode, call backing-file write helpers, and update FUSE write attributes through `fuse_passthrough_end_write()`.
- `fuse_passthrough_open()` validates a positive backing id, looks up `struct fuse_backing`, opens a per-FUSE-file backing file using `backing_file_open()`, and stores backing file plus credentials in `struct fuse_file`.
- Release closes the backing file and drops credentials.

Dependencies and integration:
- Depends on Linux backing-file helpers and FUSE backing-id registry.
- Called from `iomode.c` when `FOPEN_PASSTHROUGH` is accepted.

Risks and invariants:
- A separate backing file is opened per FUSE file to preserve the FUSE path context.
- Write paths deliberately serialize with `inode_lock()`.
- `fuse_passthrough_release()` expects `ff->passthrough` and `ff->cred` to be initialized.
