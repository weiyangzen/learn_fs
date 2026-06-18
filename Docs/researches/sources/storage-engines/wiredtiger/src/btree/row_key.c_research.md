# sources/storage-engines/wiredtiger/src/btree/row_key.c

## Purpose
`row_key.c` reconstructs and optionally instantiates row-store leaf keys. Row-store pages may store keys directly, as overflow references, as instantiated `WT_IKEY` copies, or prefix-compressed against earlier keys. This file supplies the slow-path logic used when the fast inline key accessor cannot directly return a complete key.

## Important APIs, Types, And Functions
- `__wt_row_leaf_key_copy` returns a stable copied key.
- `__wt_row_leaf_key_work` reconstructs a key and optionally installs an instantiated copy in the page.
- `__wt_row_ikey_alloc`, `__wti_row_ikey_incr`, and `__wti_row_ikey` allocate/install `WT_IKEY` objects.
- Key structures and helpers include `WT_ROW`, `WT_IKEY`, `WT_CELL_UNPACK_KV`, `WT_ROW_KEY_COPY`, `__wt_row_leaf_key_info`, and `__wt_dsk_cell_data_ref_kv`.

## Control Flow
The slow path starts at the requested row slot and rolls backward looking for a usable uncompressed or instantiated non-overflow key. If it finds a direct non-prefix key or non-overflow instantiated key, it may switch to forward reconstruction. Overflow keys cannot provide a prefix base for other keys, so they are skipped as bases. If the requested key itself is overflow, the code reads it under `btree->ovfl_lock` and retries if reconciliation changed the cell to removed-overflow while the page had an instantiated replacement.

For prefix-compressed keys, the code may use the page's prefix group root (`prefix_start`/`prefix_stop`) to reconstruct directly. Otherwise it records a backward jump point where prefixes shrink, then rolls forward from a base key, repeatedly truncating the buffer to the prefix length and appending suffix bytes until it reaches the target slot.

If `instantiate` is requested, the reconstructed key is copied into a new `WT_IKEY` and installed with an atomic compare-and-swap into the row slot. On success, the page memory footprint is increased; on race loss, the allocated key is freed.

## State And Persistence Behavior
The file changes only in-memory page state by optionally replacing row key references with instantiated `WT_IKEY` objects and increasing cache memory accounting. It reads overflow key data from disk/block cache when needed but does not alter persisted content.

## Dependencies And Integration Points
Row key reconstruction is used by row search, verification, debugging, and modification paths that need full keys from a leaf. It depends on row page memory layout, cell unpacking, overflow locking, block-cache cell data reads, atomic pointer updates, and cache accounting. Diagnostic builds assert that instantiated keys are not overwritten and are not installed after a ref has split.

## Risks
Prefix-compressed reconstruction is easy to get wrong around overflow keys, mixed instantiated/on-page keys, and concurrent overflow removal. The code explicitly copies row key references because they may change underfoot. Installing instantiated keys must account for races with other threads and page splits. Buffer management must preserve prefixes while growing and appending suffixes.

## Test Signals
Tests should cover direct on-page keys, copied keys, prefix-compressed keys requiring backward then forward reconstruction, prefix group reconstruction, overflow requested keys, overflow keys used as non-bases, concurrent overflow removal/retry, repeated random search instantiation, reverse cursor instantiation behavior, and races where another thread instantiates the key first.
