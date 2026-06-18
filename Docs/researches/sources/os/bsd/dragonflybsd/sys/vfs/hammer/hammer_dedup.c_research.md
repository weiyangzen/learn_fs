# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_dedup.c

## Role

Implements the HAMMER deduplication ioctl path for replacing one duplicate data block reference with another while updating blockmap reference accounting.

## Main Entry Point

- `hammer_ioc_dedup()` receives two B-tree leaf descriptors from userspace, validates both records, compares their data, adjusts blockmap accounting, frees the second block reference, and repoints the second leaf to the first data offset.

## Control Flow

- Requires filesystem version `HAMMER_VOL_VERSION_FIVE` or newer because version 5 allows dedup accounting through signed `bytes_free`.
- Initializes `cursor1`, looks up the first element, and extracts data.
- Initializes `cursor2`, looks up the second element, and extracts data.
- Validates both leaves point to data zones, not metadata zones.
- Requires both data offsets to be in the same HAMMER zone and both data lengths to match.
- Performs a byte-by-byte `bcmp()` before modifying metadata.
- Acquires the shared sync lock and upgrades both cursors together with `hammer_cursor_upgrade2()`, which handles shared nodes correctly.
- Calls `hammer_blockmap_dedup()` on the first block to increment/rebalance dedup accounting.
- Invalidates cursor2’s cached data buffer before freeing its old data block, then calls `hammer_blockmap_free()`.
- Modifies cursor2’s B-tree leaf `data_offset` to point at cursor1’s data block.
- Downgrades both cursors, releases the sync lock, and cleans up cursors.

## Error and Status Semantics

- Unsupported filesystem version returns `EOPNOTSUPP`.
- Lookup/extract/upgrade failures return errors so userspace can retry candidates later.
- Invalid zones set `HAMMER_IOC_DEDUP_INVALID_ZONE` and return success.
- Data mismatch, zone mismatch, or length mismatch set `HAMMER_IOC_DEDUP_CMP_FAILURE` and return success.
- Blockmap underflow sets `HAMMER_IOC_DEDUP_UNDERFLOW` and returns success.
- Other blockmap errors propagate.

## Pressure Handling

After cursor cleanup, the function waits/kicks the flusher while metadata pressure or undo exhaustion is above background thresholds. This avoids deadlocking the buffer cache during bulk dedup runs.

## Research Notes

This is a compact ioctl implementation, but it relies heavily on cursor correctness, blockmap accounting, and buffer invalidation. The ordering around `hammer_cursor_invalidate_cache()` before freeing cursor2’s old block is a key safety detail.
