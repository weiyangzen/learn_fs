# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_io.c

## Purpose
Provides HAMMER2's device I/O abstraction (`hammer2_io_t`) over DragonFly buffer-cache buffers. It maps smaller logical allocations into 64KB physical buffers, handles read/new/write lifecycle, tracks dirty state, caches DIO objects in a hash table, and records dedup-validity bits.

## DIO Hashing and Allocation
- `hammer2_io_hash_init()` initializes per-device DIO hash spinlocks.
- `hammer2_io_alloc()` maps a `data_off|radix` to a 64KB physical base, looks for an existing DIO, or creates one when requested.
- It validates that the logical allocation fits within one 64KB physical buffer and resolves the backing volume/device via `hammer2_get_volume()`.
- DIO refs use low bits as a reference count plus high state flags such as GOOD, INPROG, WAITING, DIRTY, and FLUSH.
- Reusing a free DIO decrements `hmp->iofree_count`; creating a new one increments global DIO count.

## Buffer Acquisition
- `_hammer2_io_getblk()` handles read, new-zeroed, new-nonzero, and quick-read operations.
- If a DIO is already GOOD, it returns immediately after optional zeroing/dirty marking.
- Otherwise it atomically owns `INPROG`, waits on concurrent owners as needed, and performs `getblk()`, `breadnx()`, or `cluster_readx()` depending on operation and clustering settings.
- Metadata and data reads use separate tunables (`hammer2_cluster_meta_read`, `hammer2_cluster_data_read`), and data buffers are tagged `B_NOTMETA`.
- New allocations can avoid reads when logical allocation exactly matches the physical DIO; partial-new operations read first and then zero/dirty the requested range.
- Buffers are synchronized for KVA access with `bkvasync()` and associated with the kernel process via `BUF_KERNPROC()`.

## Buffer Release and Writeback
- `_hammer2_io_putblk()` decrements references. On the last reference, it clears GOOD/DIRTY, marks INPROG, detaches the buffer, and then releases or schedules writeback.
- Dirty DIOs normally use delayed write (`bdwrite`) to accumulate writes and avoid chain-lock-driven write/read churn.
- If `HAMMER2_DIO_FLUSH` is set, dirty DIOs use clustered write or async write depending on write clustering tunables.
- Clean buffers are released by `bqrelse()` unless error/invalidation flags require `brelse()`.
- DIO objects remain cached after buffer release; `iofree_count` drives cleanup pressure.
- `_hammer2_io_bawrite()`, `_hammer2_io_bdwrite()`, and `_hammer2_io_bwrite()` set dirty/flush flags then drop the DIO.

## Public Helpers
- `hammer2_io_new()` creates a zeroed DIO range.
- `hammer2_io_newnz()` creates a DIO range without zeroing the target data.
- `_hammer2_io_bread()` reads a DIO range.
- `_hammer2_io_getquick()` returns a DIO only if already cached.
- `hammer2_io_data()` returns a pointer to the logical range within the physical buffer.
- `hammer2_io_setdirty()` marks an already-held DIO dirty.
- `hammer2_io_bkvasync()` synchronizes a held buffer for KVA access.
- `_hammer2_io_ref()` adds a reference to an already-owned DIO.
- `hammer2_io_inval()` is currently a no-op placeholder for destroyed metadata invalidation.

## Dedup Tracking
- `hammer2_io_dedup_set()` creates/references a DIO without needing a buffer and marks dedup allocation bits while clearing validation bits.
- `hammer2_io_dedup_delete()` clears allocation and validation bits for data blocks when allocations are destroyed or bulkfree invalidates candidates.
- `hammer2_io_dedup_assert()` asserts no dedup allocation bits are set for a range, useful for transitions to free.
- Dedup operations are synchronized with freemap allocation/free state through the DIO object rather than the buffer cache buffer.

## Cleanup
- `hammer2_io_hash_cleanup()` scans hash buckets, ages inactive DIOs via `act` and `ticks`, removes free non-INPROG DIOs, and frees them outside locks.
- `hammer2_io_hash_cleanup_all()` destroys every DIO for a media device during teardown and asserts no buffer or live ref remains.

## Important Constraints
- `pbase` must be nonzero and the logical extent must not cross a 64KB physical buffer.
- Last-drop handling must coordinate with concurrent getters through INPROG/WAITING bits.
- Dirty accounting is updated only if the buffer was not already delayed-write.
- Cached DIOs can persist after their buffers are released, preserving dedup state and enabling cheaper reuse.
