# sources/storage-engines/wiredtiger/src/include/serial_inline.h

## Purpose
Implements inline serialized insertion and update paths for page skip lists and update chains, including column-store append record allocation, page dirtying, cache footprint accounting, newest timestamp heuristics, and obsolete update checks.

## Important APIs, Types, And Functions
- `__insert_simple_func` CAS-inserts a `WT_INSERT` into already-linked skiplist positions without taking the page lock.
- `__insert_serial_func` inserts into a skiplist with validation and tail maintenance.
- `__col_append_serial_func` allocates record numbers for append operations and updates `btree->last_recno`.
- `__wt_page_modify_update_timestamp` stores the approximate newest seen global timestamp into page modify state.
- `__wt_col_append_serial` serializes column-store append insertion, cache accounting, dirty marking, and timestamp update.
- `__wt_insert_serial` serializes row/column insertions, using the simple lock-free path when possible.
- `__wt_update_serial` CAS-inserts a `WT_UPDATE` into an update chain, validates transaction rules on races, updates cache/dirty/timestamp state, and may trim obsolete updates.

## Control Flow
Insert helpers read each target skiplist pointer once with an acquire barrier, validate it still matches `new_ins->next[i]`, and CAS in the new insert. Failure at level zero returns `WT_RESTART`; upper-level failure returns success because lower levels are sufficient. Append logic assigns a new record number when the caller used `WT_RECNO_OOB`, positions insert stacks at tails, inserts, and updates `last_recno`. Public insert/append wrappers take the page lock unless the caller has exclusive access, transfer ownership of allocated memory, free it on error, then update cache footprint and dirty state after publication.

Update serialization repeatedly CASes a new update onto the chain; if it loses a race, it revalidates with `__wt_txn_modify_check` before retrying. After publication it updates cache and dirty state, skips obsolete checks under configured conditions/history store/exclusive access/short chains, may advance oldest transaction state, avoids ingest garbage collection races, and finally calls `__wt_update_obsolete_check`.

## State And Persistence Behavior
These helpers mutate in-memory page insert lists, update chains, btree `last_recno`, page cache footprint, dirty state, and page modify timestamps. They prepare changes that later reconciliation/checkpoint can persist. They also influence eviction by timestamp and obsolete-update metadata.

## Dependencies And Integration Points
Depends on page locks, skiplist structures, atomics/barriers, transaction visibility/modify checks, cache accounting, page modify state, history-store detection, eviction controls, btree flags, and session/connection timestamp state. Integrated with cursor insert/update/modify paths and reconciliation/eviction.

## Risks
Memory ordering is critical: structure setup must be visible before list publication. Lost upper skiplist levels are tolerated but reduce skiplist efficiency. Ownership transfer means callers must not free `*new_insp`/`*updp` after calling. Obsolete trimming after insertion must not race with history store or ingest btree readers. Updating `last_recno` assumes rightmost-page locking discipline.

## Test Signals
Concurrency tests should stress insert/update races, `WT_RESTART` behavior, append record allocation, skiplist tail maintenance, cache footprint accounting, dirty marking, timestamp heuristic updates, obsolete update trimming, history-store exceptions, and exclusive versus locked paths.
