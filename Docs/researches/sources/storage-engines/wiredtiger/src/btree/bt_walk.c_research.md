# sources/storage-engines/wiredtiger/src/btree/bt_walk.c

## Purpose
`bt_walk.c` implements WiredTiger's generic in-memory btree traversal primitive. It moves a caller's `WT_REF *` forward or backward through the tree, optionally skipping internal/deleted/cache-miss pages, invoking custom skip callbacks, counting visited refs, and protecting traversal with hazard pointers and page-index generations while concurrent splits and eviction occur.

## Important APIs, Types, And Functions
- `__wt_tree_walk` moves to the next or previous page.
- `__wt_tree_walk_count` also reports a reference-visit count.
- `__wt_tree_walk_custom_skip` lets callers provide a skip function such as checkpoint cleanup.
- `__wti_tree_walk_skip` skips a requested number of leaf pages.
- `__tree_walk_internal` is the shared traversal engine.
- `__split_prev_race` detects split races that can cause backward walks to skip namespaces.
- Key types are `WT_REF`, `WT_PAGE_INDEX`, `WT_REF_STATE`, and read flags such as `WT_READ_PREV`, `WT_READ_CACHE`, `WT_READ_SKIP_INTL`, `WT_READ_NO_WAIT`, `WT_READ_TRUNCATE`, `WT_READ_VISIBLE_ALL`, and `WT_READ_SEE_DELETED`.

## Control Flow
The shared walker asserts it can reason about visibility, derives default deleted-page skipping unless rollback-to-stable or explicit see-deleted is active, saves the original ref, enters the page-index generation, and starts from the root if no ref is active. It then uses slot arithmetic to descend to the next leaf or ascend/post-order-return internal pages depending on direction and flags.

When descending, it checks current ref state, cache-only/no-wait restrictions, truncate deletion opportunities, visibility of deleted pages, and caller skip callbacks. It swaps hazard pointers with `__wt_page_swap`, returning leaves immediately and coupling through internal pages. On `WT_NOTFOUND`, it treats cache misses/deleted races as expected. On `WT_RESTART`, it releases coupled pages and restarts from the original position/root. On backward walks, `__split_prev_race` validates parent/child page-index consistency and restarts when internal splits could otherwise make the traversal choose the wrong predecessor.

At completion or error, it logs very slow walks, releases the coupled page and original ref, leaves the page-index generation, and returns the resulting page in `*refp` or `NULL` at end-of-walk.

## State And Persistence Behavior
The walker is in-memory only, but it controls access to pages that persistence operations depend on. Hazard pointers prevent eviction of the returned page and coupled ancestors during movement. It may mark empty internal pages for eviction and may invoke fast-delete logic in truncate mode. It updates `pindex_hint` opportunistically to speed later slot lookup.

## Dependencies And Integration Points
Tree walking is used by checkpoint sync, eviction, verification, checkpoint cleanup, compaction, truncate, and cursor scans. It depends on page-swap/read code, hazard pointer release, page-index generation macros, split race helpers, delete-page visibility helpers, prefetch, eviction scheduling, transaction visibility flags, and read-generation flags.

## Risks
The highest-risk behavior is concurrent split handling. Forward walks and backward walks have different safety properties, and the backward path has explicit race detection to avoid skipped namespaces. Misused flags can accidentally read pages into cache, skip deleted pages needed by rollback/truncate, or return internal pages to callers that expect leaves only. Error cleanup must release both the original and coupled refs exactly once.

## Test Signals
Tests should exercise forward and backward cursor walks across internal splits, append workloads, cache-only checkpoint walks, truncate walks that fast-delete pages, rollback-to-stable walks that see deleted refs, custom skip callbacks, leaf-skip counting, empty internal page eviction hints, and long-walk warning behavior. Concurrency stress with page splits and eviction is especially important.
