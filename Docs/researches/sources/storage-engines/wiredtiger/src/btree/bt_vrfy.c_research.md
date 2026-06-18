# sources/storage-engines/wiredtiger/src/btree/bt_vrfy.c

## Purpose
`bt_vrfy.c` implements logical btree verification for WiredTiger files and checkpoints. It coordinates block-manager verification, loads each checkpoint root, recursively validates tree structure and page relationships, verifies row/column key ordering, validates time aggregates and time windows, checks overflow references, optionally verifies history-store consistency, and includes disaggregated-storage checks for checkpoint size and page discard.

## Important APIs, Types, And Functions
- `__wt_verify(WT_SESSION_IMPL *, const char *cfg[])` is the main verify entry point.
- `WT_VSTUFF` carries verification configuration, scratch buffers, progress counters, layout counters, stable timestamp, and deferred read-corrupt errors.
- `__verify_config` and `__verify_config_offsets` parse verify/dump options.
- `__verify_tree` recursively verifies logical tree consistency after physical disk-image verification has loaded a page.
- `__verify_page_content_int` and `__verify_page_content_leaf` validate cells, timestamps, overflow items, and history-store ranges.
- `__verify_row_int_key_order` and `__verify_row_leaf_key_order` enforce row-store ordering across depth-first traversal.
- `__wt_verify_disagg_database_size`, `__verify_disagg_accumulate_size`, and `__verify_page_discard` validate disaggregated metadata invariants.
- `__verify_unique_btree_ids` checks stable constituent files in metadata for duplicate btree IDs.

## Control Flow
`__wt_verify` asserts checkpoint and schema locks are held, allocates scratch buffers, parses configuration, optionally dumps requested block offsets, and checks stable-file btree ID uniqueness. It obtains the checkpoint list and starts block-manager verification. For each non-fake checkpoint, it resets per-checkpoint state, loads the checkpoint root address, opens the checkpoint tree if non-empty, prints dump information when requested, and releases the file-exclusive eviction lock while doing recursive verification.

`__verify_tree` is depth-first. It logs page metadata, tracks tree shape, optionally dumps disk/page details, validates that page type matches btree type, checks column record-number ordering or row leaf ordering, validates child write generations, verifies page content, checks parent address-cell type versus page type, and descends into internal children. Child descent unpacks address cells, validates timestamp aggregates, accumulates disaggregated block sizes, reads the child with `__wt_page_in`, optionally continues after read failures under `read_corrupt`, recursively verifies, releases the child page, and asks the block manager to verify the address.

After the most recent checkpoint, verify may check disaggregated page discard and history-store consistency. The checkpoint is unloaded, eviction exclusivity is restored, and the loaded tree is discarded before moving to the next checkpoint.

## State And Persistence Behavior
Verify is mostly read-only, but it temporarily swaps checkpoint roots into the btree handle and uses eviction/file-discard operations to clean that in-memory state between checkpoints. It accumulates `records_so_far`, largest row key/address, tree-depth counters, and disaggregated block-size totals per checkpoint. With `read_corrupt`, it records the first read error in `vs->verify_err` and continues traversal where possible, returning the deferred error after cleanup.

## Dependencies And Integration Points
This verifier depends on block-manager verify hooks (`verify_start`, `verify_addr`, `verify_end`, checkpoint load/unload, page-id enumeration), metadata checkpoint list APIs, page read/build paths, disk-image physical verification from `bt_vrfy_dsk.c`, row key helpers, time-window validation, history-store verification, verbose/debug dump utilities, eviction exclusivity, and disaggregated-storage metadata. It is a central consumer of btree page layout invariants produced by reconciliation.

## Risks
Verification runs in a sensitive mode: it has an exclusive handle but repeatedly loads and unloads checkpoint roots while allowing eviction for memory pressure. Missing an eviction exclusivity transition can expose invalid roots. Key ordering logic depends on correct handling of internal 0th keys, corrupted first leaves, custom collators, and prefix/overflow keys. Stable timestamp checks are optional but strict when enabled. The disaggregated checkpoint-size comparison is currently disabled behind `if (false)` because known reconciliation edge cases can produce mismatch noise.

## Test Signals
Strong tests include corrupted child write generation, illegal page type for btree type, row internal and leaf key-order violations, column record-number ordering violations, invalid timestamp aggregates/time windows, bad overflow references, stable timestamp violations, duplicate stable btree IDs, history-store mismatch, read-corrupt traversal behavior, disaggregated page discard mismatch, and dump-mode diagnostic builds. The unit hook `__ut_verify_compare_page_id_lists` directly exercises page-id list comparison.
