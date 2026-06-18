# sources/storage-engines/wiredtiger/src/include/block.h

## Purpose
This header defines the default and disaggregated block-manager data structures, persistent block formats, checkpoint extent metadata, and the `WT_BM` vtable used by btree code to read, write, checkpoint, compact, salvage, verify, and sync pages.

## Important APIs, Types, And Functions
Core types include `WT_EXTLIST`, `WT_EXT`, and `WT_SIZE` for checkpoint allocation/free/discard extent management; `WT_BLOCK_CKPT` for checkpoint cookies and extent lists; `WT_BM` for the block-manager method table; `WT_BLOCK` for local file-backed block handles; `WT_BLOCK_DESC` and `WT_BLOCK_HEADER` for ordinary on-disk headers; `WT_BLOCK_DISAGG`, `WT_BLOCK_DISAGG_HEADER`, and `WT_BLOCK_DISAGG_ADDRESS_COOKIE` for disaggregated page-log storage. Iterator macros such as `WT_EXT_FOREACH`, `WT_EXT_FOREACH_OFF`, and `WT_EXT_FOREACH_FROM_OFFSET_INCL` define extent traversal.

## Control Flow
This file is declarative, but its vtable defines the control surface used throughout the engine. Btree code calls `WT_BM` methods for address validation/stringification, checkpoint start/load/resolve/unload, read/write/read_multiple, free, compaction, salvage, verification, object switching, mapping, stats, sync, and write-size alignment. Extent-list macros drive block allocation and verification code by walking skiplist heads in offset or size order.

## State And Persistence Behavior
Many definitions are persistent format contracts. Offset zero is invalid because the description block lives at the first block. `WT_BLOCK_DESC`, `WT_BLOCK_HEADER`, and `WT_BLOCK_DISAGG_HEADER` sizes and flag values cannot change without disk compatibility impact. `WT_BLOCK_CKPT` models the checkpoint's root address, allocated/available/discarded extents, file size, checkpoint size, and archived checkpoint extents. Disaggregated address cookies persist page id, flags, LSNs, cumulative size, and checksum for base/delta chains.

## Dependencies And Integration Points
The header integrates with `btmem.h` page headers, block manager implementation files, btree reconciliation, checkpoint metadata, compaction, salvage, verification, tiered/multi-handle objects, and disaggregated storage. It depends on skiplist depths, file handles, checksums, time/address metadata, page block metadata, and storage abstractions such as bucket storage or page log through associated structs.

## Risks
Disk-format sensitivity is high. Changing field order, sizes, magic values, header flags, or checkpoint cookie layout can break existing databases. `WT_BLOCK` and `WT_BLOCK_DISAGG` must keep a shared prefix; violating that breaks code that treats them generically. Extent skiplist nodes appear on multiple lists, so incorrect depth/offset handling can corrupt free-space accounting. Multi-handle arrays require locking discipline.

## Test Signals
Use static layout assertions, endian tests, checkpoint round trips, salvage over corrupt blocks, verification of extent overlap/fragment maps, compaction rewrite accounting, multi-object/tier switch tests, disaggregated base/delta checksum chains, and backward-compatibility tests that open older files.
