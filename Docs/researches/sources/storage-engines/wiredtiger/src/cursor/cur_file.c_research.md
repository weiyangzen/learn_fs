# sources/storage-engines/wiredtiger/src/cursor/cur_file.c

## Purpose
`cur_file.c` is the primary `WT_CURSOR_BTREE` implementation for file-backed WiredTiger objects. It adapts the public `WT_CURSOR` API to btree cursor primitives, handles checkpoint cursor transaction substitution, supports bulk load and random cursors, manages cursor caching/reopen, and enforces cursor state invariants around position, key, and value flags.

## Important APIs, Types, and Functions
The main exported entry points are `__wt_curfile_open`, `__wt_cursor_checkpoint_id`, and `__wt_curfile_insert_check`. `__curfile_create` installs the method table for btree cursors: compare, equals, next, prev, reset, search, search_near, insert, modify, update, remove, reserve, reconfigure, largest_key, bound, cache, reopen, checkpoint ID, and close. Most methods validate cursor state with helpers such as `__cursor_checkkey`, `__cursor_checkvalue`, and `__cursor_copy_release`, then dispatch to `__wt_btcur_*` operations.

The `WT_WITH_CHECKPOINT` macro is a key piece of this file. It temporarily substitutes a checkpoint dummy transaction into `session->txn`, disables reconciliation, sets the matching history-store checkpoint name, and swaps checkpoint write generation while performing a checkpoint cursor operation. `__curfile_setup_checkpoint` constructs that dummy transaction from `WT_CKPT_SNAPSHOT` metadata and records the history-store checkpoint dhandle and checkpoint ID.

## Control Flow
`__wt_curfile_open` parses `bulk`, `checkpoint_wait`, and `checkpoint_use_history`; obtains the btree/checkpoint dhandle via `__wt_session_get_btree_ckpt`; and passes any matching history-store handle and checkpoint snapshot metadata into `__curfile_create`. Bulk cursors require exclusive access, are disallowed inside transactions, and initialize `WT_CURSOR_BULK`. Random cursors replace the operation table with a limited `next_random`/`reset` surface and seed the btree cursor RNG.

Normal read operations enter the cursor API, check overload and transaction/checkpoint restrictions, optionally wrap btree access in `WT_WITH_CHECKPOINT`, and assert resulting key/value state. Write operations use update API wrappers, measure write latency histograms, and call btree insert/update/modify/remove/reserve. `remove` preserves the special API semantic that a positioned remove remains positioned and rolls back if that initial position is lost. `reserve` repeats a search after the reserve so callers can fetch a value.

Close first tries cursor-cache release, then frees bulk resources, closes the btree cursor, releases checkpoint transaction and history-store handles, frees cursor memory, decrements dhandle use, and releases the dhandle unless the cursor was reopened from a dead handle. Cache and reopen mirror normal file handle lifecycle and reset URI/format fields if the btree handle was reopened.

## State and Persistence Behavior
This file does not implement page storage itself; persistence is delegated to btree modify/search/truncate/reconciliation layers. It does, however, control persistent access mode through dhandle locking, bulk-load flags, checkpoint snapshot metadata, and transaction visibility setup. Checkpoint cursors read a stable historical view by pairing data-store checkpoint metadata with the correct history-store checkpoint and dummy transaction. Cursor state is tracked through `WT_CURSTD_*` flags and `WT_CBT_ACTIVE`; many assertions document which methods should leave the cursor positioned.

## Dependencies and Integration Points
`cur_file.c` integrates with session dhandle lookup/release, checkpoint metadata, transaction timestamp parsing, history-store checkpoint opening, btree cursor primitives, cursor cache infrastructure, bulk cursor support, statistics, random cursor support, and bound handling. It is the underlying child cursor for table, index, dump, history-store, and layered implementations whenever they need ordinary btree access.

## Risks and Edge Cases
Checkpoint cursor correctness is the highest-risk area because it relies on matching data-store checkpoints, history-store checkpoints, snapshot transaction arrays, stable/oldest timestamps, and write generations. Reopen/cache paths must not release dead handles incorrectly. Bulk open interacts with checkpoint locks and exclusive dhandle access. `remove` has subtle retry behavior when a prepared conflict or restart loses a starting position. `largest_key` temporarily changes `WT_CURSTD_KEY_ONLY` and resets the cursor twice; failures must restore state. Bound setting is rejected on positioned cursors, and largest-key is incompatible with bounds.

## Test Signals
Coverage is spread across cursor, checkpoint, bulk, random, bounded cursor, and format workloads. Direct signals include bulk cursor tests and format bulk paths, random cursor tests, bounded cursor suites, checkpoint read timestamp/config coverage, and insert-check use from checkpoint metadata code. Additional targeted tests should stress checkpoint cursors that read history-store values, reopen cached cursors after handle replacement, positioned remove retry behavior, and reserve followed by `get_value`.
