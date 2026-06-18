# sources/storage-engines/wiredtiger/src/block/block_ckpt_scan.c

## Purpose
This file supports standalone recovery/import of WiredTiger files by embedding final metadata/checkpoint information in the last avail-list block and scanning a file to recover the newest such checkpoint.

## Important APIs, Types, and Functions
`__wti_block_checkpoint_final` appends write generation, placeholder file size, metadata, checkpoint-list string, and incomplete checkpoint cookie to the final avail-list buffer. `__wt_block_checkpoint_last` scans for the latest final checkpoint block and returns recovered metadata, checkpoint list, and corrected checkpoint cookie. `__block_checkpoint_update` patches the recovered cookie with actual avail-list address/checksum and file size.

## Control Flow
Checkpoint finalization extends the avail-list buffer, writes an incremented btree write generation, reserves packed file-size space, appends length-prefixed metadata/checkpoint/cookie payloads, aligns capacity, and returns the reserved file-size pointer. Scanning walks candidate blocks, validates reads/checksums, filters for block-manager extent lists with `WT_BLOCK_EXTLIST_VERSION_CKPT`, unpacks payloads, keeps the highest generation fully read, patches the cookie, and returns owned strings to the caller.

## State and Persistence Behavior
The appended payload persists inside a block-manager extent-list page and is read-only during recovery. Scratch buffers and recovered strings are allocated in memory.

## Dependencies and Integration Points
The file depends on block headers, extent-list pair encoding, variable integer packing, block read/checksum validation, metadata checkpoint format, progress reporting, and checkpoint packing.

## Risks and Edge Cases
Tiered tables are not supported. Scanning intentionally ignores many invalid blocks. Correctness relies on write-generation monotonicity and the extent-list version marker. Partial payloads are skipped. The file-size placeholder must be patched before checksum/write.

## Test Signals
Tests should recover the highest-generation final checkpoint, reject files without one, tolerate corrupt candidates, and verify patched avail address/checksum/file-size fields.
