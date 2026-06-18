# File Research: sources/local-fs/xfsprogs/libxfs/rdwr.c

## Role

`rdwr.c` is the userspace libxfs buffer-cache, block-device I/O, and log-formatting layer. It adapts kernel-style `xfs_buf` usage to xfsprogs, including cache lookup, buffer locking, verifier dispatch, dirty writeback, delayed-write submission, raw device zeroing, and clean-log initialization.

The file explicitly documents that userspace buffer error semantics differ from the kernel: many callers leave `bp->b_error` uncleared, so release and dirty-mark paths clear stale errors to avoid leaking old read/write failures into later cache hits.

## Major Responsibilities

- Zero device ranges with `fallocate(FALLOC_FL_ZERO_RANGE)` when possible, falling back to aligned zero-buffer writes.
- Fetch primary and realtime superblock buffers through `libxfs_getsb` and `libxfs_getrtsb`.
- Implement cache hashing, key comparison, allocation, release, bulk release, flushing, purging, and overflow checks for `xfs_buf`.
- Allocate and initialize cached, mapped, discontiguous, and uncached buffers.
- Provide optional pthread-based buffer locking with recursion detection for userspace repair paths.
- Read and verify buffers via single-map or multi-map I/O, including salvage mode for callers that want corrupt buffers returned.
- Write dirty buffers through verifiers and `pwrite`, including discontiguous-map writes and mem-backed targets.
- Maintain dirty/stale/unchecked/uptodate buffer state and prevent stale buffers from being written.
- Submit or cancel delayed-write buffer lists synchronously.
- Format a clean/unmount log image with `libxfs_log_clear` and `libxfs_log_header`.
- Verify 16-bit and 32-bit metadata magic values against buffer verifier tables.
- Flush device write caches through `platform_flush_device`.
- Mark buffers corrupt for non-verifier relationship corruption with `__xfs_buf_mark_corrupt`.

## Buffer Cache Flow

The cache key is `struct xfs_bufkey`, containing target, start block, length, and optional maps. `libxfs_bhash` hashes by disk block, and `libxfs_bcompare` returns hit only if both block and length match. A same-block length mismatch can purge the old entry, with optional diagnostics under `IO_BCOMPARE_CHECK`.

Allocation reuses buffers from `xfs_buf_freelist` when possible. `__libxfs_getbufr` prefers a freelist buffer of matching byte size; otherwise it reuses another buffer after freeing its data and non-inline map storage, or allocates a new cache object. `__initbuf` resets core fields, allocates aligned memory, zeros contents, initializes lock state, and sets a single default map unless discontiguous maps are supplied.

`__cache_lookup` obtains or allocates a cache node, then optionally locks the buffer. If the caller requests `LIBXFS_GETBUF_TRYLOCK`, lock contention returns `-EAGAIN`; recursive locking by the same thread increments `b_recur` after warning.

## Read And Verify Path

`libxfs_buf_read_map` first finds a cached buffer. If it is already uptodate or dirty and marked `LIBXFS_B_UNCHECKED`, supplied verifier ops are run before returning it. On a cache miss it reads with `libxfs_readbufr` or `libxfs_readbufr_map`, sets `LIBXFS_B_UPTODATE` on successful reads, and calls `libxfs_readbuf_verify`.

The `LIBXFS_READBUF_SALVAGE` flag allows a buffer to be returned even if verification fails. This is important for repair-style callers that need to inspect damaged metadata.

## Writeback Path

`libxfs_bwrite` refuses to write stale buffers, runs an optional mount writeback hook, clears stale preexisting errors, runs write verifiers, and writes either a single contiguous buffer or each discontiguous map. Successful writes mark buffers uptodate and clear dirty/unchecked flags; failed writes print block, length, and verifier-name diagnostics.

`libxfs_buf_mark_dirty` clears stale errors, clears the stale flag, and marks the buffer dirty and uptodate. Dirty cached buffers are written by cache flush or during release of uncached buffers.

## Log Formatting

`libxfs_log_clear` zeroes an on-disk or memory log, writes the initial clean log record, and optionally fills the rest of the log with previous-cycle records so kernel log head/tail discovery sees a clean log. `libxfs_log_header` builds v1/v2 log record headers, extended cycle headers for large v2 records, an unmount transaction record, cycle-data packing, and cycle-stamped padding blocks.

## Notable Assumptions

- Memory buftargs skip physical reads and writes.
- Uncached buffers are recognized by an empty cache-node hash list and a direct refcount.
- Release paths clear `b_error` to compensate for legacy userspace callers.
- Dirty buffers reaching the free list are treated as lost/corrupt write evidence and set buftarg flags.
- Several allocation and I/O failures print diagnostics and `exit(1)`, reflecting xfsprogs utility behavior rather than kernel-style propagation.
