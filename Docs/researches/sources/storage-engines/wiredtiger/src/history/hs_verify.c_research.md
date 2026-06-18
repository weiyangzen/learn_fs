# sources/storage-engines/wiredtiger/src/history/hs_verify.c

## Purpose
This file verifies history-store consistency. Its core invariant is that there must not be a history-store entry for a key unless the corresponding key exists in the data store. It supports verifying one btree with exclusive access and verifying all history-store ids across the connection.

## Important APIs, Types, And Functions
`__wt_hs_verify_one` verifies a single btree id. It opens an HS cursor, positions to the first record for that btree id, opens a raw btree cursor directly with `__wt_btcur_init` and `__wt_btcur_open`, then delegates to `__hs_verify_id`. `__wt_hs_verify` is the public all-HS entry point; it iterates ids via `__wt_curhs_next_hs_id` and calls `__hs_verify`. `__hs_verify` scans the selected HS table, resolves btree ids to data-store URIs, opens the corresponding data-store cursor, and calls `__hs_verify_id` for each id run. `__hs_verify_id` walks HS keys for a single btree id and searches the data store for each distinct key.

## Control Flow
`__hs_verify_id` assumes the HS cursor is already positioned. For each HS record with the target btree id, it compares the key with the previously checked key and skips duplicate versions. For row-store it calls `__wt_row_search`; for column-store it unpacks the recno and calls `__wt_col_search`, both under `WT_WITH_PAGE_INDEX`. If the data-store cursor comparison says the key was not found, it marks `WT_CONN_DATA_CORRUPTION` and panics with a formatted key message. It resets the data-store cursor between keys and leaves the HS cursor either at the next btree id or EOF.

`__hs_verify` handles whole-HS traversal. On disaggregated followers it opens shared stable history-store and data-store checkpoints rather than live stable handles, because followers cannot dirty pages and live reads can trigger leader-only assertions when stop-timestamp records are reinstantiated.

## State And Persistence Behavior
Verification is read-only unless corruption is detected, in which case it sets `WT_CONN_DATA_CORRUPTION` and panics. It sets cursor flags such as `WT_CURSTD_HS_READ_COMMITTED`, `WT_CURSTD_IGNORE_TOMBSTONE`, and `WT_CURSOR_RAW_OK` to make verification see the necessary physical content. No HS records are added or removed.

## Dependencies And Integration Points
The file depends on HS cursor APIs, metadata btree-id-to-URI lookup, row and column btree search, checkpoint metadata lookup, raw cursor behavior, page-index generation protection, and connection disaggregation state. It complements the generic verify command by checking the cross-file invariant between HS entries and data-store keys.

## Risks
The verifier intentionally panics on mismatches, so false positives are severe. Duplicate HS versions for one key must be skipped correctly to avoid redundant work. Column-store key unpacking must match HS key encoding. Disaggregated follower logic must choose checkpoints consistently; otherwise verification may compare HS and data-store snapshots from different generations. Cursor ownership is error-prone because `__hs_verify_id` moves the HS cursor for its caller.

## Test Signals
Test one-tree and all-HS verification, empty HS tables, duplicate HS versions per key, missing datastore keys, row-store and column-store keys, metadata id lookup failures, disaggregated leader and follower checkpoint paths, no-checkpoint follower early returns, and cleanup of data/HS cursors after corruption and normal EOF.
