<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btree_inline.h -->
# sources/storage-engines/wiredtiger/src/include/btree_inline.h

## Purpose
Collects performance-critical inline B-tree helpers for page state, dirty tracking, cache accounting, row-key access, address copying, eviction eligibility, hazard-pointer release, skiplist depth selection, page-index navigation, and disaggregated-storage accounting. This header sits in the core execution path for reads, writes, checkpoint, reconciliation, eviction, and cursor traversal.

## Important APIs, Types, and Functions
Bulk and page-state helpers include `__wt_btree_disable_bulk`, `__wt_page_is_empty`, `__wt_page_evict_clean`, `__wt_page_is_modified`, `__wt_page_is_reconciling`, `__wt_page_dirty_and_evict_soon`, and `__wt_btree_block_free`.

Cache accounting helpers include `__wt_btree_bytes_inuse`, `__wt_btree_bytes_evictable`, dirty/update byte accessors, `__wt_cache_page_inmem_incr`, `__wt_cache_page_inmem_decr`, `__wt_cache_dirty_incr_size`, `__wt_cache_dirty_decr_size`, `__wt_cache_dirty_decr`, image accounting, and shared disk image accounting. The decrement helpers `__wt_cache_decr_check_size` and `__wt_cache_decr_check_uint64` clamp underflow to zero, log the accounting bug, and abort in diagnostic builds.

Dirty-state APIs include `__wt_page_modify_init`, `__wt_page_only_modify_set`, `__wt_tree_modify_set`, `__wt_page_modify_clear`, `__wt_page_modify_set`, and `__wt_page_parent_modify_set`. They coordinate page dirty state, tree/connection modified flags, cache dirty counters, first dirty transaction tracking, and checkpoint ordering.

Row-store and reference key APIs include `__wt_ref_key`, `__wt_ref_key_onpage_set`, `__wt_ref_key_instantiated`, `__wt_ref_key_clear`, `__wt_row_leaf_key_info`, `__wt_row_leaf_key_set`, `__wt_row_leaf_value_set`, `__wt_row_leaf_key_free`, `__wt_row_leaf_key`, `__wt_row_leaf_key_instantiate`, `__wt_row_leaf_value_is_encoded`, `__wt_row_leaf_value`, and `__wt_row_leaf_value_cell`. These use pointer bit encodings to avoid unpacking common on-page keys and simple values.

Address, deletion, and eviction helpers include `__wt_ref_addr_copy`, `__wt_get_page_modify_ta`, `__wt_ref_block_free`, `__wt_page_del_visible_all`, `__wt_page_del_visible`, `__wt_page_del_committed_set`, `__wt_btree_syncing_by_other_sessions`, `__wt_leaf_page_can_split`, `__wt_page_evict_retry`, `__wt_materialization_check`, `__wt_btree_can_discard`, `__wt_btree_disagg_checkpointed`, `__wt_page_can_evict`, and `__wt_page_release`.

Traversal helpers include `__wt_skip_choose_depth`, `__wt_split_descent_race`, `__wt_page_swap_func`, `__wt_btcur_bounds_early_exit`, `__wt_btcur_skip_page`, `__wt_ref_index_slot`, and `__wt_ref_ascend`.

## Control Flow
Modification starts by allocating `page->modify`, marks the tree dirty, atomically transitions the page from clean to dirty, updates cache counters only for the first dirty transition, records first dirty transaction state, and marks the tree dirty again to cover checkpoint races. The metadata and history-store special case can pre-increment dirty counters for low dirty-leaf counts to avoid temporary negative cache accounting under low isolation.

Memory accounting increments and decrements per-connection cache totals, per-btree totals, page footprint, internal-page totals, dirty bytes, update bytes, image bytes, and disaggregated ingest/stable sub-counters. Decrement paths use guarded subtraction and tolerate races by limiting dirty/update byte decrements to the observed page-local amount.

Row-key access first decodes the pointer tag. Internal keys use a one-bit tag distinguishing allocated `WT_IKEY` from encoded on-page offset/length. Leaf keys use two low bits to distinguish direct cell offsets, encoded key metadata, encoded key/value metadata, and instantiated keys. `__wt_row_leaf_key` returns direct on-page data when possible, builds keys from a page-level prefix group when possible, and falls back to `__wt_row_leaf_key_work` for overflow or complex prefix-compressed cells.

Eviction eligibility is a sequence of blockers and fast exits: prefetched refs, read-only trees, disaggregated materialization frontier, uncommitted fast truncation, checkpoint-related overflow-key constraints, possible in-memory split, clean disaggregated pages ahead of materialization, dirty pages during another session's checkpoint, dirty internal disaggregated pages, current disaggregated checkpoint generation, active split generations for internal pages, and metadata pages with recently modified data. `__wt_page_release` uses that result either to queue urgent eviction, attempt release-and-evict, or clear the hazard pointer.

Tree traversal helpers detect non-atomic internal split races by comparing saved parent page indexes, ensure page-in/page-release coupling does not leak hazard pointers, and search parent indexes from ref hints with backoff until split updates stabilize.

## State and Persistence Behavior
The header mutates in-memory `WT_BTREE`, `WT_PAGE`, `WT_PAGE_MODIFY`, `WT_REF`, `WT_CACHE`, and connection flags/counters. It affects persistence indirectly by controlling when pages and trees are marked dirty, when disk blocks are freed, which address cookies are copied, and whether checkpoint/eviction can reconcile or discard content. Disaggregated storage adds materialization-frontier state, checkpoint generation state, stable/ingest cache buckets, and shared disk-image byte tracking.

## Dependencies and Integration Points
This file depends on atomic primitives, hazard pointers, generation tracking, transaction visibility, timestamps, reconciliation state, cache structures, eviction functions, block manager callbacks, salvage tracking, cursor bounds comparison, row/column page macros, overflow handling through cell unpacking, and disaggregated/layered table manager state. It is integrated with update insertion, checkpoint, eviction server/app eviction, B-tree search, cursor next/prev, truncate, page split, reconciliation, block free, and cache pressure calculations.

## Risks and Edge Cases
The dirty-state ordering is delicate: page content must become visible before page/tree dirty markers, and tree dirty markers must not race checkpoint into losing dirty pages. Cache accounting races are expected; underflow guards prevent wraparound but can leave cache usage conservative. Pointer-tag encodings assume allocated memory alignment and page-size bit budgets; unusual page sizes or misaligned allocations would break fast-path decoding. `__wt_ref_addr_copy` requires a split generation and uses ordered reads to avoid pairing a new home page with an old on-page address. Eviction blockers are correctness-sensitive for checkpoint, disaggregated materialization, uncommitted truncation, overflow-key history, and internal split generations.

## Test Signals
Strong signals include eviction and checkpoint stress tests, dirty/clean page accounting tests, metadata/history-store update tests, disaggregated storage materialization and checkpoint tests, in-memory split tests, row-store prefix compression and overflow-key tests, hazard-pointer traversal tests, truncate visibility tests, cache accounting diagnostics, and stress flags for release eviction, checkpoint eviction races, and skiplist depth.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/btree_inline.h -->
