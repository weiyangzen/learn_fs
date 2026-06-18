# sources/storage-engines/wiredtiger/src/cursor/cur_prepared_discover.c

## Purpose
Implements the prepared-transaction discovery cursor. The cursor enumerates prepared transaction IDs discovered during recovery or prepared-discovery setup, allowing callers to claim or inspect outstanding prepared work.

## Important APIs, types, and functions
The entry point is `__wt_cursor_prepared_discover_open`, which creates a `WT_CURSOR_PREPARE_DISCOVERED` with key format `Q` and no value columns. `__cursor_prepared_discover_setup` applies prepared-discovery filtering to handles, then populates the cursor list. `__cursor_prepared_discover_list_create` copies prepared IDs from `S2C(session)->txn_global.pending_prepare_items` into a cursor-owned, zero-terminated array. Cursor methods are intentionally narrow: `next`, `reset`, and `close` are supported; value, search, update, compare, and reverse iteration are not.

## Control flow
Open allocates the cursor, installs methods, and runs setup under checkpoint and schema locks to keep the metadata and prepared-artifact view consistent. `next` checks whether the cursor list exists and whether the current slot is nonzero, packs the prepared ID into the cursor key buffer using the `Q` format, advances the array index, and marks the key internal. `reset` rewinds the index and clears key/value flags. `close` frees the cursor list and then walks any remaining pending-prepared hash buckets, treating them as unclaimed transactions.

## State, persistence, and dependencies
Cursor-owned state is the copied prepared-ID array, list allocation, and next index. Connection-owned state is `WT_TXN_GLOBAL.pending_prepare_items`, a hash table of `WT_PENDING_PREPARED_ITEM` entries with modification arrays. The cursor close path frees unclaimed transaction operation arrays via `__wt_txn_op_free`; claimed items are expected to have been removed by other prepared transaction claim logic before close.

## Integration points
The file is tied to prepared transaction recovery and discovery, transaction-global prepared maps, schema/checkpoint locks, and standard cursor API wrappers. It provides a cursor API facade around connection-level prepared transaction metadata rather than over a btree.

## Risks and test signals
The close path deliberately errors if unclaimed prepared transactions remain, so ownership transfer and cleanup ordering are critical. Tests should verify empty discovery, multiple hash buckets, reset-and-rescan behavior, key packing format, claimed-item removal by other sessions, unclaimed cleanup error reporting, and lock interaction with schema/checkpoint activity. The TODO about a prepared transaction discovery read/write lock is a concurrency risk signal.
