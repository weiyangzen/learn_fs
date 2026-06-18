# sources/storage-engines/wiredtiger/src/block/block_ext.c

## Purpose

`block_ext.c` owns WiredTiger block-manager extent-list mechanics: allocation, freeing, merging, overlap reconciliation, extent-list read/write, truncation eligibility, and diagnostic dumping. It is the allocator's in-memory model of file-space state, tracking live `alloc`, `avail`, `discard`, and checkpoint-derived lists as ordered skip lists.

## Important APIs, Types, and Functions

The central types are `WT_BLOCK`, `WT_EXTLIST`, `WT_EXT`, and `WT_SIZE`. `WT_EXTLIST` stores extents by offset and, when `track_size` is enabled, by size to support best-fit allocation. Important exported/internal-entry functions are `__wti_block_alloc`, `__wt_block_free`, `__wti_block_off_free`, `__wti_block_off_remove_overlap`, `__wti_block_extlist_overlap`, `__wti_block_extlist_merge`, `__wti_block_extlist_read_avail`, `__wti_block_extlist_read`, `__wti_block_extlist_write`, `__wt_block_extlist_can_truncate`, `__wti_block_extlist_truncate`, `__wti_block_extlist_init`, `__wti_block_extlist_free`, and `__wti_block_extlist_dump_all`.

Local helpers implement skip-list operations: `__block_off_srch`, `__block_size_srch`, `__block_off_srch_pair`, `__block_ext_insert`, `__block_off_remove`, `__block_append`, and `__block_merge`. `WT_BLOCK_RET` converts extent corruption into verify errors while panicking in normal operation.

## Control Flow

Allocation requires `block->live_lock`, validates allocation-size alignment, chooses first-fit by offset or best-fit by size, removes or shrinks an available extent, and records the allocation in `live.alloc`. If no suitable range exists, `__block_extend` advances `block->size` and appends to the allocation list.

Freeing unpacks an address cookie, ignores old tiered object IDs, and under `live_lock` routes the range through `__wti_block_off_free`. Ranges allocated in the current checkpoint are removed from `live.alloc` and immediately returned to `live.avail`; older ranges are merged into `live.discard` so checkpoint resolution can decide when they are reusable.

Extent-list persistence writes a block-manager page with packed offset/size pairs bracketed by `WT_BLOCK_EXTLIST_MAGIC` and `WT_BLOCK_INVALID_OFFSET`. Reads validate alignment and checkpoint file bounds before rebuilding skip lists. Available-list reads remove the block occupied by the extent-list page itself.

## State and Persistence Behavior

The file mutates in-memory file-space state (`block->size`, `WT_EXTLIST.entries`, `bytes`, `last`, offset/size skiplists) and persists checkpoint extent lists as pages in the same data file. `live.alloc`, `live.avail`, `live.discard`, `live.ckpt_avail`, and per-checkpoint extents encode the durable allocator history used across checkpoints. Truncation removes a terminal available extent and calls `__wti_block_truncate`, making free-at-end space disappear from both memory and the underlying file.

## Dependencies and Integration Points

The code integrates with address-cookie unpacking in `block_addr`, raw block I/O in `block_read.c`/`block_write.c`, checkpoint code in `block_ckpt.c`, compaction/truncation code, salvage and verify paths, session-local extent allocation caches from `block_session.c`, and WiredTiger stats/verbose logging. It relies on callers to hold `live_lock` for live list mutation except salvage.

## Risks and Edge Cases

Extent-list overlap is a correctness boundary: overlap in normal operation panics, while verify returns an error. Incorrect lock ownership can corrupt skip lists. Size-list and offset-list indexes must stay synchronized on every insert/remove. Old tiered objects currently cannot reclaim freed blocks, so free tracking for non-current object IDs is ignored. Large or fragmented available lists can make first-fit scans expensive, though the code records search walk time.

## Test Signals

Diagnostic builds exercise misplaced-block checks and list-overlap panics. Unit-test shims expose skip-list search, insert, remove, append, merge, and allocation helpers. Runtime signals include `block_alloc`, `block_free`, `block_extension`, `block_reuse_bytes`, extent-list verbose dumps, verify-layout output, and corruption paths that dump all extent lists.
