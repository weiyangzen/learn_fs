# sources/storage-engines/wiredtiger/src/block/block_write.c

## Purpose

`block_write.c` implements physical writes to file-backed block handles. It aligns page images to allocation units, allocates file space, optionally extends/truncates OS-visible file size, computes block checksums, writes disk blocks, updates cache/fsync behavior, and returns address-cookie components.

## Important APIs, Types, and Functions

Important functions are `__wti_block_truncate`, `__wti_block_discard`, `__wt_block_write_size`, `__wt_block_write`, `__wti_block_write_off`, and private `__block_extend`/`__block_write_off`. It manipulates `WT_BLOCK_HEADER`, `WT_PAGE_HEADER`, `WT_BLOCK.size`, `extend_size`, `extend_len`, `os_cache`, and `WT_FH.written`.

## Control Flow

`__wt_block_write_size` adds the block-manager header and rounds up to `block->allocsize`, rejecting sizes near 4 GiB. `__wt_block_write` calls `__wti_block_write_off`, then packs `(objectid, offset, size, checksum)` into an address cookie. `__wti_block_write_off` byte-swaps the page header around the internal write so callers keep native-order page images.

The internal write optionally adds final-checkpoint recovery data, aligns size, preallocates extent nodes, acquires `live_lock` if needed, allocates space through `__wti_block_alloc`, optionally extends the file outside the lock when supported, zeros alignment padding, initializes the block header, computes either full-data or prefix checksum, writes to the file handle, frees the allocation on write failure, optionally fsyncs dirty OS cache, discards from OS cache, updates statistics, and returns offset/size/checksum.

## State and Persistence Behavior

Successful writes persist an endian-normalized block header plus page image bytes to the data file and mutate allocator state by consuming/creating extents. `block->size` is advanced before the actual write, and failures free the allocated range back through allocator logic. `__wti_block_truncate` updates in-memory size even when physical truncate is unsupported or temporarily busy, because truncation is an optimization rather than a correctness requirement.

## Dependencies and Integration Points

This file depends on extent allocation/freeing, checkpoint-final metadata, address packing, capacity throttling, file-system write/extend/truncate/fsync/advise hooks, hot-backup locks, OS cache settings, and block-cache write wrappers that handle compression/encryption before physical writes.

## Risks and Edge Cases

File extension can release `live_lock`, so callers must honor the `caller_locked` contract. `block->size` can move ahead of durable writes, making failure cleanup essential. Prefix checksums rely on compression/encryption layers to detect payload corruption. Truncation and extension are skipped during hot backup and tolerate `EBUSY`/`ENOTSUP`. Incorrect buffer sizing before alignment is treated as a caller bug.

## Test Signals

Signals include allocation-size rounding, oversized write rejection, write-failure cleanup, full versus prefix checksum reads, hot-backup truncate/extend suppression, OS dirty-cache fsync scheduling, `block_write` and `block_byte_write_checkpoint` stats, and final checkpoint writes that patch file-size metadata.
