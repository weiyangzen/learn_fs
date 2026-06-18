# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_io.c

This file implements FreeBSD FUSE file data I/O. It bridges vnode/buffer-cache operations to `FUSE_READ` and `FUSE_WRITE` requests, supporting direct I/O, buffered I/O, clustered read/write, dirty buffer writeback, and cache invalidation.

Key responsibilities:
- Defines `B_FUSEFS_WRITE_CACHE`, a buffer flag indicating that a write originates from cache writeback and lacks the original user credential/pid context.
- Implements buffered reads in `fuse_read_biobackend`.
  - Validates nonnegative offset.
  - Gets file size through `fuse_vnode_size`.
  - Uses `bread`, `breadn`, or `cluster_read` depending on EOF proximity, sequentiality, mount flags, and daemon read-ahead limit.
  - Copies buffer data into the caller `uio`.
  - Treats short reads as EOF.
- Implements direct reads in `fuse_read_directbackend`.
  - Repeatedly sends `FUSE_READ` sized by `uio_resid` and `data->max_read`.
  - Sets file handle, offset, read size, and ABI 7.9+ read flags.
  - Moves daemon response bytes directly into caller `uio`.
  - Stops on short read.
- Implements direct writes in `fuse_write_directbackend`.
  - Handles append by using the passed file size.
  - Applies file-size rlimit through `vn_rlimit_fsizex`.
  - Splits writes into `data->max_write` chunks.
  - Builds ABI-sensitive `fuse_write_in`.
  - Sets `FUSE_WRITE_CACHE` when write origin is cache-like or writeback data.
  - Handles signal/interruption after `uiomove` by rewinding `uio` as far as possible and converting `ERESTART` to `EINTR`.
  - Warns and fails if daemon reports writing more bytes than sent.
  - Handles short writes:
    - warns when short write happens without `direct_io`;
    - for direct I/O returns the unwritten part to caller;
    - for cached writes retries the unwritten tail.
  - Updates vnode size and dirty timestamp state when writes extend the file.
- Implements buffered writes in `fuse_write_biobackend`.
  - Validates regular vnode, offset, and residual.
  - Reads current size, handles append, checks rlimit.
  - Uses `getblk` to acquire or create buffers.
  - Extends vnode size before writing into a newly extended buffer to avoid reader races.
  - Performs read-modify-write when needed.
  - Tracks dirty byte ranges in buffers and writes out existing discontiguous dirty regions before accepting a new noncontiguous write.
  - Chooses `bwrite`, `bawrite`, `cluster_write`, or `bdwrite` based on sync/direct/async/cache pressure and full-block coverage.
- Implements `fuse_io_strategy`, the actual buffer strategy backend.
  - Requires regular files or directories and `BIO_READ`/`BIO_WRITE`.
  - Resolves a read or write FUSE file handle.
  - Allows a read-modify-write read using a write handle when the file was opened write-only.
  - For reads, calls direct backend, zero-fills unread tail, and clears attr cache on clean short reads.
  - For writes, writes only the dirty range through direct backend, preserving dirty buffers on `EINTR`/`ETIMEDOUT` so they can be retried.
- Implements buffer flush/invalidation helpers:
  - `fuse_io_flushbuf` delegates to `vn_fsync_buf`.
  - `fuse_io_invalbuf` serializes invalidations with `FN_FLUSHINPROG`/`FN_FLUSHWANT`, cleans VM pages, calls `vinvalbuf`, and handles interruptible waits.

Integration points:
- Uses file handles from `fuse_file.h`.
- Uses vnode state and size helpers from `fuse_node.c`.
- Uses dispatcher IPC from `fuse_ipc.c`.
- Used by vnode read/write/strategy paths outside this group and by invalidation logic in `fuse_internal.c`.

Notable risks and research hooks:
- The code has multiple cache-coherency defenses but still depends on daemon correctness for file size and short-write behavior.
- `FUSE_WRITE_CACHE` means the daemon may not know the real writer identity for cached writes.
- Buffered writeback preserves dirty buffers on timeout/interruption, so repeated daemon failures can leave dirty state pending.
- A comment in `fuse_node.h` says direct I/O is tracked on vnode state even though it should be per file handle.
- Clean short reads clear attr cache rather than truncating immediately to avoid lock-order problems.
