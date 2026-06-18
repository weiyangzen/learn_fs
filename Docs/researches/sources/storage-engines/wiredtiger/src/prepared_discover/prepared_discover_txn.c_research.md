<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_txn.c -->
# sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_txn.c

## Purpose
Maintains pending prepared-transaction artifacts discovered during recovery/checkpoint walking, including restoration to ingest tables for disaggregated followers.

## Important APIs, Types, and Functions
`__wt_prepared_discover_find_item`, `__wt_prepared_discover_remove_item`, `__wti_prepared_discover_add_artifact_upd`, and `__wti_prepared_discover_restore_and_add_artifact_upd`. Helpers allocate prepared `WT_UPDATE`s and initialize the pending-prepared hash map.

## Control Flow
Find hashes `prepared_id` into a power-of-two bucket. Find-or-create lazily initializes a 256-bucket map, allocates `WT_PENDING_PREPARED_ITEM`, and inserts it. Adding an artifact allocates the next pending transaction op and records the update with btree/key context. Restoration builds an in-progress prepared update from an on-disk time window, searches/modifies the ingest btree under the ingest dhandle, then registers the artifact.

## State and Persistence Behavior
Updates in-memory transaction-global pending prepared state. In disaggregated follower mode it also writes restored updates into the ingest table so later prepare resolution can commit/rollback them.

## Dependencies and Integration Points
Integrates with transaction global state, update allocation, row search/modify, pending prepared op arrays, ingest/stable layered tables, and prepare timestamp/ID fields.

## Risks and Edge Cases
Stop-prepare tombstones are represented as standard updates carrying a special tombstone value because ingest cannot accept tombstones in this flow. Remove asserts `mod_count == 0`, so ownership transfer must be complete. Cursor hazard release before reused searches is critical.

## Test Signals
Prepared recovery tests, disaggregated follower stable-to-ingest restoration, stop-prepare handling, hash collisions, and pending item removal assertions are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/prepared_discover/prepared_discover_txn.c -->
