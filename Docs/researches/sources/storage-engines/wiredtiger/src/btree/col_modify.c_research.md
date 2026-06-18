# sources/storage-engines/wiredtiger/src/btree/col_modify.c

## Purpose
`col_modify.c` implements column-store insert, update, delete, reserve, tombstone, append, and update-chain restoration on a pinned column-store leaf page. It creates or prepends `WT_UPDATE` chains, allocates column `WT_INSERT` skiplist nodes, serializes insertion into page modification structures, and records successful cursor writes in the transaction operation log.

## Important APIs, Types, And Functions
- `__wt_col_modify` is the column-store modification entry point.
- `__col_insert_alloc` allocates a record-number keyed `WT_INSERT` with skiplist next pointers.
- Important structures include `WT_CURSOR_BTREE`, `WT_PAGE`, `WT_PAGE_MODIFY`, `WT_INSERT_HEAD`, `WT_INSERT`, `WT_UPDATE`, and transaction/session state.
- It calls shared serialization APIs: `__wt_update_serial`, `__wt_insert_serial`, and `__wt_col_append_serial`.

## Control Flow
The function validates that the caller supplied either a value to allocate an update, an existing update/list, or a reserve/tombstone request. It ensures the page has a modify structure. If no update list is supplied, it detects append operations when the recno is out of band or beyond the leaf's last record and clears cursor insert/search state.

If the search found an existing insert for the exact record, the code allocates or prepends updates, checks transaction modify conflicts, records a transaction update, links the new update to the old chain, and serializes the update-chain head swap. If no exact insert exists, it chooses the append list or per-slot update list, allocates an insert head if necessary, allocates a skiplist node, creates or attaches the update chain, initializes skiplist next pointers from cursor search stacks, and serializes either append or normal insertion.

After the update is linked, cursor-originated non-reserve changes are logged with `__wt_txn_log_op`, and append operations record the assigned recno in the transaction operation for prepared transaction lookup.

## State And Persistence Behavior
This file mutates in-memory update chains and insert lists; persistence happens later via reconciliation and logging. It updates page memory through serialized insertion functions and transaction state through `__wt_txn_modify`. Append insertion may allocate the final record number in `__wt_col_append_serial`, then stores it in transaction state. `prev_durable_ts` on new updates records conflict-check history for timestamp rules.

## Dependencies And Integration Points
Column modify depends on prior column search state (`cbt->compare`, `cbt->slot`, `cbt->ins`, `cbt->ins_head`, search stacks), page modify allocation, update allocation, transaction conflict checks, transaction logging, skiplist depth selection, and rollback cleanup. It is used by cursor operations, range truncate patterns, update restore eviction, and internal update-list restoration.

## Risks
The tricky paths are append detection, updating a record inside a run-length encoded on-page cell where `ins_head` exists but `ins` does not, and error ownership after updates are linked into page memory. Once an update is inserted into the chain, rollback logic owns cleanup; freeing it locally would corrupt page state. Restoration paths assert that existing chains are empty or contain only allowed prepared-restored content. Concurrent insert/update races depend on the serialization functions and correctly initialized search stacks.

## Test Signals
Tests should cover appends with `WT_RECNO_OOB`, updates beyond the last on-page record, updates inside RLE cells, tombstone/reserve writes, restore of full update chains, conflict detection against existing updates, transaction log failure after linking, exclusive versus non-exclusive insert serialization, and rollback cleanup after partial failure.
