# sources/storage-engines/wiredtiger/src/btree/bt_compact.c

## Purpose
Implements btree compaction by walking internal pages, asking the block manager which referenced blocks are worth moving, rewriting selected disk addresses or marking clean in-memory pages dirty, and forcing checkpoints/eviction to materialize improved layout.

## Important APIs, types, and functions
- `__wt_compact` is the file-level compaction entry point.
- `__compact_walk_internal` reviews one internal page under the btree flush lock.
- `__compact_page` locks a `WT_REF`, rewrites on-disk addresses through the block manager, or delegates in-memory review.
- `__compact_page_inmem` and `__compact_page_inmem_check_addrs` decide whether an in-memory page should be rewritten.
- `__compact_page_replace_addr` installs a rewritten block cookie while preserving address time-window metadata.
- `__compact_walk_page_skip` makes the tree walk visit internal pages only.

## Control flow
`__wt_compact` first asks `bm->compact_skip` whether the file has useful compaction work. If not, it increments skip stats and logs once per table. Otherwise it repeatedly checks interruption/cache-stuck state, throttles by helping eviction, walks to the next internal page using `WT_READ_INTERNAL_OP`, `WT_READ_VISIBLE_ALL`, and `WT_READ_WONT_NEED`, and calls `__compact_walk_internal` while the page index is stable.

For each internal page, `__compact_walk_internal` acquires `flush_lock` to avoid racing checkpoint review. It visits child leaf refs and calls `__compact_page`. If no leaf moved and the parent is not root, it may compact the internal page itself. When any page is selected, it marks the parent/tree dirty and sets `session->compact_state = WT_COMPACT_SUCCESS`.

`__compact_page` locks the ref. Disk/deleted refs with addresses are passed to `bm->compact_page_rewrite`; if the block manager returns a new address, `__compact_page_replace_addr` swaps it in. In-memory clean pages have their original/replacement/multiblock addresses checked by `bm->compact_page_skip`; selected pages are marked modified and tagged `WT_PAGE_COMPACTION_WRITE`.

## State and persistence behavior
Compaction manipulates `WT_REF` address cookies and page dirty state rather than logical records. Rewritten addresses are installed in memory and become persistent through subsequent reconciliation/checkpoint. Address replacement preserves timestamp metadata unpacked from on-page address cells. `WT_PAGE_COMPACTION_WRITE` tells reconciliation to write new blocks. Statistics count selected in-memory pages, compact sessions, skipped files, conflicting checkpoints, eviction assistance, and reviewed pages.

## Dependencies and integration points
The file depends on the generic tree walk, hazard/ref locking, flush lock, block-manager compaction hooks (`compact_skip`, `compact_page_skip`, `compact_page_rewrite`, `compact_progress`), eviction assistance, page modification/reconciliation flags, address unpack/copy helpers, and session compact interruption checks.

## Risks and edge cases
- Holding `flush_lock` and `WT_REF` locks across block-manager checks/rewrite can block checkpoint and application work.
- Moving blocks while checkpoint is reviewing the tree could corrupt checkpoints; the flush lock is the key safety mechanism.
- In-memory dirty pages are not forced immediately because checkpoint is expected to write them eventually.
- Root pages are not directly moved as internal pages because forced checkpoint rewrites roots.
- Block-manager hooks must initialize skip outputs correctly; no-op block managers can make compaction ineffective.

## Test signals
Tests should exercise compact skip/no-work, block rewrite address replacement, in-memory clean-page selection, dirty-page handling, multiblock replacement addresses, deleted refs, checkpoint conflict/retry, interruption and cache-stuck exits, stats progress, and correctness after a checkpoint following compaction.
