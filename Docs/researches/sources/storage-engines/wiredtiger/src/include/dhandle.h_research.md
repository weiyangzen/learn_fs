# sources/storage-engines/wiredtiger/src/include/dhandle.h

## Purpose
`dhandle.h` defines WiredTiger data handles: named, lockable references to btrees, tables, tiered objects, metadata, and other data-source handles. It also provides macros for safely swapping a session's current handle and tracking handle lifecycle/debug state.

## Important APIs, Types, and Functions
Context macros include `WT_WITH_DHANDLE`, `WT_WITH_BTREE`, `WT_WITHOUT_DHANDLE`, and `WT_SAVE_DHANDLE`. `WT_DHANDLE_CLEAR` clears `session->dhandle` while recording source location in a circular `WT_DHANDLE_CLEAR_LOG`. `WT_DHANDLE_ACQUIRE`, `WT_DHANDLE_RELEASE`, and `WT_DHANDLE_NEXT` manage reference counts while walking handle queues.

`WT_DATA_HANDLE` contains locking (`rwlock`, `close_lock`), queue/hash links, URI/checkpoint identity, metadata config and hashes, reference/use counts, exclusive-session fields, data-source pointer, generic handle pointer, type, stats arrays, lifecycle flags, timestamp assertion flags, lock flags, and advisory eviction flags.

## Control Flow
Schema/session code sets `session->dhandle` before operating on an object and restores it afterward using the context macros. The connection keeps handles in both list and hash queues; walkers use `WT_DHANDLE_NEXT` under handle-list locks to acquire/release references as they progress. Exclusive operations use the handle rwlock and flags to prevent concurrent opens/closes.

## State and Persistence Behavior
The handle itself is in-memory but mirrors durable object identity and metadata configuration. `meta_base`, hashes, checkpoint names/orders, and timestamp flags describe persisted metadata state. `references`, `session_inuse`, `timeofdeath`, and lifecycle flags drive when handles can be swept, reopened, discarded, or marked dead.

## Dependencies and Integration Points
This header integrates with sessions, btrees, metadata cursors, connection dhandle queues, tiered work units, cached cursors, statistics, schema operations, and checkpoint/open/close paths. It depends on atomic helpers, queue macros, and lock primitives.

## Risks and Edge Cases
Reference/use-count ordering is critical because handles may be freed after the final decrement. `WT_DHANDLE_INACTIVE` and `WT_DHANDLE_CAN_REOPEN` encode subtle flag combinations that affect handle reuse. Macros assume appropriate locks are already held; misuse can corrupt connection queues or race with sweep/checkpoint. The clear log is debug-only aid and should not be treated as synchronization.

## Test Signals
Useful signals are schema open/close/drop/rename tests, handle sweep tests, checkpoint while closing handles, cached cursor lifetime tests, exclusive access tests, tiered handle tests, and sanitizer/thread-sanitizer coverage for reference counting.
