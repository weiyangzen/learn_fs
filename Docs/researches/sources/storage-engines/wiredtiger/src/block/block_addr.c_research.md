# sources/storage-engines/wiredtiger/src/block/block_addr.c

## Purpose
This file implements block address-cookie packing, unpacking, validation, string formatting, and checkpoint-cookie encoding/decoding for WiredTiger's block manager.

## Important APIs, Types, and Functions
`__wt_block_addr_pack` and `__wt_block_addr_unpack` convert between offset/size/checksum/object-id tuples and variable-length address cookies. `__wt_block_addr_invalid` validates cookies against file size and diagnostic extent placement. `__wt_block_addr_string` formats cookies. Checkpoint functions include `__wti_block_ckpt_unpack`, `__wt_block_ckpt_decode`, `__wti_block_ckpt_pack`, and `__wti_ckpt_verbose`.

## Control Flow
Address packing stores offset as allocation units minus one, size as allocation units, checksum, and optional object ID. A zero size encodes an invalid/empty address. Checkpoint cookies encode version, root/alloc/avail/discard addresses, file size, checkpoint size, and one optional object ID shared by all address blocks.

## State and Persistence Behavior
Packed cookies are persistent on-disk metadata. Their encoding depends on `block->allocsize`, so decoding requires the correct block context. Object IDs support tiered storage references while preserving zero-object compatibility.

## Dependencies and Integration Points
The file depends on variable integer helpers, `WT_BLOCK`, `WT_BLOCK_CKPT`, verbose logging, and extent-list/checkpoint consumers. It is used by block I/O, checkpointing, verify, salvage, compaction, and external decode utilities.

## Risks and Edge Cases
Cookie compatibility is critical. The checkpoint path's address-size-zero special case suppresses object-ID parsing and is subtle. Validation only bounds addresses for the current object. Future flags must preserve consumed-byte assertions.

## Test Signals
Round-trip empty/non-empty addresses, object ID zero/non-zero, multiple allocation sizes, unsupported checkpoint versions, verbose formatting, and file-size boundary validation.
