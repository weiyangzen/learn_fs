# sources/storage-engines/wiredtiger/src/btree/bt_random.c

## Purpose

`bt_random.c` implements random row-store cursor positioning and random page descent for `WT_CURSOR.next_random` and eviction sampling. It chooses random leaf pages, samples on-disk row slots or insert skip lists, and falls back to cursor movement when deletion-heavy or tiny pages make direct random selection unreliable. The complete 634-line source was read for this report.

## Important APIs, Types, and Functions

The main entry point is `__wt_btcur_next_random`, which validates row-store support, initializes cursor state, chooses random descent or leaf-skip sampling, and returns through `__cursor_kv_return`. `__wt_random_descent` walks internal pages from the root to a random leaf, with separate behavior for normal sampling and eviction (`WT_READ_CACHE`). Leaf helpers include `__random_leaf`, `__random_leaf_disk`, `__random_leaf_insert`, `__random_leaf_skip`, `__random_skip_entries`, `__random_insert_valid`, and `__random_slot_valid`. `__random_root_inmem_ref` reservoir-samples in-memory root children for eviction sampling.

## Control Flow

`__wt_btcur_next_random` clears key/value state, disables diagnostic order checks, and first tries `__wt_random_descent` when there is no current ref or when sampling size is zero. A successful descent calls `__random_leaf`. If descent cannot find a usable page, it falls back to `__wti_tree_walk_skip`, estimating skip distance from file size, allocation size, and `next_random_sample_size`; if no ref is found, it finally calls normal `__wt_btcur_next`.

`__random_leaf` prefers large on-disk populations, then large insert lists, then a second disk attempt for moderately populated pages. If all fail, it moves next/previous a random number of records and avoids returning the immediately previous key once.

## State and Persistence Behavior

The code mutates cursor state (`ref`, `slot`, `ins_head`, `ins`, `compare`, `tmp`, random sample counters, and RNG state) but writes no persistent data. It may schedule pages for eviction when large insert skip lists make repeated random lookup expensive. It reads block-manager size metadata to estimate leaf skipping.

## Dependencies and Integration Points

It integrates with btree page/index walking, row-store key materialization, insert skip lists, visibility checks (`__wti_cursor_valid`), normal cursor next/prev paths, page swap/release, eviction scheduling, block-manager sizing, and `WT_WITH_PAGE_INDEX` split-generation protection.

## Risks and Edge Cases

Sampling is approximate and can be biased by large insert lists, uneven leaf sizes, deleted records, and file-size-based skip estimates. The skip-list estimate assumes WiredTiger's skip-list probability. Tiny or all-deleted trees force slow fallback paths. Concurrent split/eviction races rely on correct `WT_RESTART`, `WT_NOTFOUND`, and page-index handling.

## Test Signals

Cover empty/single-record/tiny trees, deletion-heavy row stores, insert-list-only pages, mixed disk and insert records, unbalanced trees, eviction random sampling, concurrent splits/eviction/checkpoints, duplicate-avoidance behavior, and `ENOTSUP` on column-store objects.
