# File Research: sources/local-fs/linux-apfs-rw/transaction.c

## Purpose

`transaction.c` implements APFS transaction lifecycle management. It reads checkpoint ephemeral objects, starts transactions under the container write lock, tracks dirty inodes and buffers, writes ephemeral objects and checkpoint maps, commits new checkpoints, schedules delayed commits, and aborts failed transactions by forcing the container read-only.

## Checkpoint And Ephemeral Objects

`apfs_read_ephemeral_objects()` allocates the in-memory ephemeral object list and reads checkpoint mapping blocks from the descriptor ring. Each mapping is loaded by `apfs_read_single_ephemeral_object()`, which supports objects up to two blocks, handles checkpoint data-ring wraparound, verifies checksums unconditionally, and records object data by oid.

`apfs_write_ephemeral_objects()` writes all in-memory ephemeral objects to the new checkpoint data ring, creates checkpoint mapping blocks in the descriptor ring, handles full mapping blocks, reserves the final descriptor slot for the new NX superblock, and updates checkpoint descriptor/data ring indexes and lengths.

`apfs_checkpoint_end()` writes the final NX superblock block after all other dirty data has been submitted, sets its xid and checksum, flushes the backing block device mapping before and after writing, and thereby commits the checkpoint.

## Transaction Start

`apfs_transaction_start()` takes `nx_big_sem` for write, rejects read-only containers, lazily reads ephemeral objects, increments the container xid for the first nested start, reads the spaceman, checks coarse free-space reservations by transaction kind, and CoWs/maps the volume superblock, volume omap, and catalog for write access.

If there is not enough reserved room, it forces a commit of existing work to flush queues and returns `-ENOSPC`.

## Commit Decision And Commit Work

`apfs_transaction_commit()` either commits immediately or schedules delayed commit work after 100 ms. Immediate commit is required when explicitly forced, transaction buffer/start thresholds are exceeded, free queues get large, internal-pool free queue pressure rises, or main free queue btree node limits are approached.

`apfs_trans_commit_work()` runs delayed forced commits under the container write lock. If it fails, it aborts the transaction.

## Commit Sequence

`apfs_transaction_commit_nx()` performs the actual checkpoint commit:

1. Flush all dirty inode metadata into buffers.
2. Flush the cached free-range record into the free queue.
3. Write dirty internal-pool bitmaps, which may modify the spaceman.
4. Write ephemeral objects and checkpoint mapping blocks.
5. Submit all transaction buffers, setting checksums for buffers marked `buffer_csum`.
6. Wait for writes and clear transaction buffer state.
7. Clean or free page-cache buffers for written non-metadata buffers.
8. End the checkpoint by writing the checksummed NX superblock.
9. Reset transaction start/buffer counters.

## Dirty Object Tracking

`apfs_inode_join_transaction()` holds an inode reference and links it into the transaction inode list. `apfs_transaction_flush_all_inodes()` repeatedly updates dirty inodes, clears raw dirty state, temporarily drops the APFS write lock around `iput()`, and detects aborts that occur during writeback.

`apfs_transaction_join()` attaches buffer heads to the transaction list, stores an `apfs_bh_info` in `b_private`, increments the buffer count, and marks `buffer_trans`.

## Abort And Read-Only Fallback

`apfs_transaction_abort()` clears transaction state, decrements the in-memory xid, clears and releases all tracked transaction buffers, forces every mounted volume in the container read-only, releases the write lock, and drops inode references from the transaction list.

The code does not attempt to undo all in-memory mutations from a failed transaction; instead, it prevents further writes to avoid committing inconsistent state.

## Invariants And Risks

- There is a single active transaction per container, guarded by `nx_big_sem`.
- Ephemeral objects are read once and rewritten with every committed transaction.
- The checkpoint superblock checksum is written last, so incomplete transactions should not become the selected checkpoint.
- Transaction buffer checksums can remain stale until commit.
- Dirty inode flushing must avoid recursive commit deadlocks.
- Abort is intentionally fail-closed and makes the container read-only.

## Test Focus

Test ephemeral object read/write with ring wraparound, checksum failures, transaction nesting, delayed commit scheduling/canceling, forced sync/unmount commits, free-space reservation behavior, dirty inode flush under concurrent eviction/writeback, buffer tracking cleanup, commit write error handling, and abort read-only enforcement across multiple mounted volumes.
