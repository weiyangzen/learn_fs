# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_wapbl.c

Read completely: 3480 lines.

Implements NetBSD's file-system independent write-ahead physical block logging layer, WAPBL. It manages per-mount journal state, transaction admission, metadata buffer capture, log record emission, stable-storage ordering, log truncation, replay discovery, and replay writes.

Core journal model:
- `struct wapbl` tracks the log vnode/device, physical log start, log/fs block shifts, circular log layout, head/tail offsets, transaction buffer accounting, committed-entry accounting, deallocation revocations, unlinked allocated inode tracking, and reusable journal I/O buffers.
- The on-disk log reserves two commit-header blocks, then uses a circular queue for block records, revocation records, and inode-list records.
- `wl_head` is advanced by `wapbl_flush()` as new records are appended; `wl_tail` is advanced by `wapbl_truncate()` when asynchronous metadata writes have completed.
- `head == tail == 0` means empty; `head == tail != 0` means full.

Initialization and teardown:
- `wapbl_start()` validates log geometry, maps the log vnode to a device block with `VOP_BMAP`, sizes in-memory transaction limits, initializes pools/hash tables/event counters, prepares commit headers, allocates journal I/O buffers, optionally preserves replay-discovered unlinked inodes, and writes an initial commit header.
- `wapbl_stop()` forces a flush, refuses to stop with persistent unlinked inodes unless forced, releases buffers and inode tracking, detaches event counters, and destroys locks/CVs.
- `wapbl_discard()` aborts in-memory journal state, invalidates pending locked buffers, clears inode/deallocation tracking, and detaches outstanding committed entries from the live journal.

Transaction path:
- `wapbl_begin()` may force a flush before admitting a reader transaction if buffered bytes, buffer count, computed transaction length, or deallocation count approaches limits.
- `wapbl_end()` asserts the transaction can fit in the usable log and drops the transaction reader lock.
- `wapbl_add_buf()`, `wapbl_remove_buf()`, and `wapbl_resize_buf()` maintain the current transaction's dirty metadata buffer list and byte/count totals.
- `wapbl_register_deallocation()` records block revocations; callers can force over-limit registration only for bounded paths.
- `wapbl_register_inode()` and `wapbl_unregister_inode()` track allocated-but-unlinked inodes so they can survive mount/log transitions.

Flush and ordering:
- `wapbl_flush()` takes the journal writer lock, invokes filesystem flush callbacks, computes transaction length, waits/truncates for space, writes block data records, revocation records, and inode records, then writes a commit header.
- After the commit header is stable, metadata buffers are issued asynchronously with `wapbl_biodone()` as completion handler.
- `wapbl_write_commit()` flushes buffered journal writes, optionally issues `DIOCCACHESYNC`, writes one of two alternating commit headers, flushes again unless FUA is used, and handles generation-zero/rollover by writing a duplicate commit.
- Disk cache behavior is controlled by sysctls for cache flush, verbose commits, DPO/FUA allowance, and journal I/O buffer count.
- `wapbl_buffered_write()` coalesces adjacent journal writes into reusable `MAXPHYS` buffers and tracks asynchronous completion.

Replay support:
- `wapbl_replay_start()` reads both commit headers, selects the newer generation, initializes replay state, builds a hash of final logged physical blocks, and records unlinked inode-list state.
- `wapbl_replay_process()` walks from tail to head, handling `WAPBL_WC_BLOCKS`, `WAPBL_WC_REVOCATIONS`, and `WAPBL_WC_INODES`.
- Block replay uses a hash keyed by filesystem block address; later block records replace earlier ones, and revocations remove blocks from replay.
- `wapbl_replay_write()` writes final logged blocks to the filesystem device.
- `wapbl_replay_can_read()` and `wapbl_replay_read()` let filesystems read blocks from the journal before full replay.

Concurrency and integration:
- Uses a rwlock for transaction readers versus flush/truncate writer operations, a mutex/CV for journal accounting, `bufcache_lock` around buffer queue transitions, and per-mount event counters.
- Integrates with `VOP_STRATEGY`, `VOP_IOCTL(DIOCGCACHE/DIOCCACHESYNC)`, `VOP_BMAP`, buffer cache I/O, module init/fini, sysctl, and filesystem-provided flush/abort callbacks.
- Kernel and non-kernel build paths share replay/log parsing helpers, with userspace allocation/assertion substitutes.

Risks and notes:
- Transaction sizing is conservative but still panics if a transaction exceeds usable log space.
- Several comments flag old assumptions or questionable behavior around circular offsets, VOP_BMAP freshness, inode-only flush skipping, and locking analysis.
- Any write or cache-flush error can permanently error the log until completion/truncation accounting clears or reports it.
- Correct crash consistency depends on strict ordering: journal records stable, commit header stable, then metadata writes.
- DPO/FUA use is disabled by default and gated behind both device cache flags and sysctl policy.
