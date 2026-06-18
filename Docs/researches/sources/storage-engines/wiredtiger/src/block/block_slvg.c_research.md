# sources/storage-engines/wiredtiger/src/block/block_slvg.c

## Purpose

`block_slvg.c` implements physical-file salvage iteration for file-backed block handles. It rewrites descriptor metadata, rebuilds a live checkpoint from pages that can still be read and validated, and frees skipped allocation-size fragments.

## Important APIs, Types, and Functions

Important functions are `__wt_block_salvage_start`, `__wt_block_salvage_end`, `__wti_block_offset_invalid`, `__wt_block_salvage_next`, and `__wt_block_salvage_valid`. It uses `WT_BLOCK.slvg_off`, `WT_BLOCK.live.alloc`, `WT_BLOCK.ckpt_state`, `WT_BLOCK_HEADER.disk_size`, address-cookie pack/unpack helpers, and raw read/free functions.

## Control Flow

Salvage start rewrites the descriptor block, initializes the live checkpoint, truncates the file to an allocation-size multiple, starts scanning after the descriptor block, places the rest of the file on `live.alloc`, and marks checkpoint state `WT_CKPT_SALVAGE`.

`__wt_block_salvage_next` reads one allocation-sized header at `slvg_off`, obtains the candidate disk size/checksum, rejects insane offsets with `__wti_block_offset_invalid`, and calls `__wti_block_read_off` to validate the full block. Invalid candidates free one allocation-size unit and advance. Valid candidates are returned as reconstructed address cookies. `__wt_block_salvage_valid` is the upper-layer feedback loop: accepted blocks advance past the full block, rejected candidates free one allocation-size unit and advance.

## State and Persistence Behavior

Salvage mutates the file descriptor, may truncate trailing garbage, rebuilds allocator state in memory, and frees skipped fragments into the live checkpoint's extent accounting. Salvage itself behaves like a checkpoint without the normal checkpoint start/resolve lifecycle; `__wt_block_salvage_end` resets state and unloads the checkpoint.

## Dependencies and Integration Points

The `WT_BM` method table in `block_mgr.c` exposes these routines to higher-level salvage. The file depends on descriptor write/open logic, checkpoint initialization/unload, extent insertion/freeing, block reads/checksums, and address-cookie packing. Tiered salvage is explicitly not implemented; object ID is forced to zero.

## Risks and Edge Cases

Salvage trusts only allocation-size stepping, so a valid page not aligned at the current scan boundary will be skipped. Rejected valid-size candidates only free one allocation-size unit rather than the candidate's full size. Because it rewrites descriptors and truncates files, it is not a read-only operation. It must avoid normal checkpoint state transitions while still leaving a coherent checkpoint for recovered pages.

## Test Signals

Signals include salvage over files with trailing garbage, checksum-corrupt blocks, valid pages after invalid fragments, upper-layer rejection through `salvage_valid(false)`, and final checkpoint unload. `WT_VERB_SALVAGE` logs skipped allocation-size chunks.
