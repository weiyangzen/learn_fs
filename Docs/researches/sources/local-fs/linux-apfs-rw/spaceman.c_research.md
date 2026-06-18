# File Research: sources/local-fs/linux-apfs-rw/spaceman.c

## Purpose

`spaceman.c` implements APFS space-manager support for this driver. It reads and maintains the ephemeral spaceman object, tracks internal-pool bitmaps, flushes APFS free queues, allocates normal blocks through chunk-info blocks and bitmaps, and reports free block counts.

## Spaceman Loading

`apfs_read_spaceman()` looks up the spaceman ephemeral object from the checkpoint mapping list, sets its xid to the current transaction, allocates or reuses the in-memory `apfs_spaceman`, reads internal-pool bitmaps on first use, reads main-device spaceman geometry, validates chunk-info limits, and flushes both internal-pool and main free queues at transaction start.

Fusion/large-device support is limited: `apfs_read_spaceman_dev()` rejects `sm_cab_count`, and the file generally operates on `APFS_SD_MAIN`.

## Internal Pool Bitmaps

The internal pool stores APFS metadata such as chunk-info bitmaps and CIBs. The driver keeps its bitmap blocks in memory:

- `apfs_read_ip_bitmaps()` reads all IP bitmap blocks.
- `apfs_write_ip_bitmaps()` writes dirty IP bitmap blocks at commit.
- Dirty IP bitmap writes rotate bitmap blocks by updating xid and bitmap-location arrays, freeing the old bitmap block into the IP free list and allocating a new one.
- `apfs_ip_find_free()`, `apfs_ip_mark_used()`, and `apfs_ip_mark_free()` find and update internal-pool allocation bits.

The free IP bitmap block list is represented by an on-disk linked list stored in variable-length arrays inside the spaceman object.

## Free Queues

APFS free queues delay block reuse by xid. This implementation flushes old free-queue records at transaction start:

- `apfs_free_queue_try_insert()` inserts a free range into either the IP queue or main queue, using ghost records for single-block extents.
- `apfs_free_queue_insert()` caches adjacent free ranges to reduce btree operations.
- `apfs_free_queue_insert_nocache()` bypasses the cache and treats unexpected free-queue fullness as corruption.
- `apfs_flush_free_queue()` repeatedly removes records older than the current xid and marks their blocks free in the IP bitmaps or main chunk bitmaps.

The main free queue node count is tracked to force commits before the queue gets too unbalanced.

## Block Allocation And Freeing

`apfs_spaceman_allocate_block()` scans chunk-info block addresses, optionally backwards to separate metadata and extents, reads each CIB, verifies checksums when requested, and asks `apfs_cib_allocate_block()` to allocate from one of its chunks.

`apfs_chunk_alloc_free()` handles both allocation and freeing within a chunk. It CoWs old chunk bitmaps and old CIBs when their xid predates the current transaction, updates chunk free counts and bitmap addresses, marks buffers dirty or checksummed as needed, and updates total free counts.

`apfs_main_free()` maps a block to chunk and CIB indexes, frees it through `apfs_chunk_free()`, updates the stored CIB address if CoW moved it, and may resume orphan cleanup if freeing enough space clears an earlier `-ENOSPC` condition.

## Free Space Reporting

`apfs_spaceman_get_free_blkcnt()` can run before the full spaceman has been initialized. It ensures ephemeral objects are loaded, locates the spaceman object, and sums free counts for main and tier2 device slots.

## Invariants And Risks

- The code assumes manageable internal-pool bitmap counts and rejects unusually large counts.
- CIB address arrays and other spaceman variable arrays are bounds-checked before access.
- Blocks freed in the current transaction are not reused until after commit.
- CIBs and chunk bitmaps from older transactions must be CoWed before mutation.
- Queue flushing intentionally stops at the current xid.
- Many corruption checks fail hard with `-EFSCORRUPTED`; abort then forces read-only state at the transaction layer.

## Test Focus

Test IP bitmap read/write rotation, free queue insertion and flushing for ghost and range records, allocation across full chunks and CIBs, backwards allocation, CoW of old CIBs and bitmaps, free-count accounting, free of already-free blocks, low-space transaction behavior, and statfs free-block reporting before write-mode spaceman initialization.
