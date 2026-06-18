# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/omt.h

## Purpose
Declares Toku's Order Maintenance Tree, a mutable ordered sequence with index-based operations, Heaviside-function searches, optional mark bits, and split/merge support.

## Important APIs, Types, And Functions
`toku::omt<omtdata_t, omtdataout_t, supports_marks>` exposes creation from empty or sorted arrays, split, merge, clone, clear, destroy, `size`, `insert`, `insert_at`, `set_at`, `delete_at`, range iteration, pointer iteration, fetch, `find_zero`, directional `find`, `memory_size`, and mark-specific `iterate_and_mark_range`, `iterate_over_marked`, `delete_all_marked`, `verify_marks_consistent`, and `has_marks`. Internal templates define subtree handles and nodes, stealing high bits for mark state when enabled.

## Control Flow
The public API presents a sequence abstraction. Searches rely on caller-provided monotonic sign functions, supporting exact, predecessor, and successor lookup. Mark-enabled trees force tree representation and use node/subtree bits to mark visited ranges and later delete marked nodes.

## State And Persistence Behavior
OMT state is in memory and alternates between array and tree representations. Array state tracks `start_idx`, `num_values`, and `values`; tree state tracks root, next free node index, and node array. No values pointed to by stored pointers are freed by `destroy`.

## Dependencies And Integration Points
Depends on Toku portability macros, race annotations, and `GrowableArray`. Locktree internals use OMTs for ordered collections such as transaction IDs, range records, and tree bookkeeping.

## Risks And Edge Cases
The API requires POD-like values and manual lifetime management. Search correctness depends on the supplied Heaviside function being monotonic. Mark bits are intentionally racy in limited cases and require exclusive access for verification and most mutation. The maximum node index is constrained by bit stealing when marks are enabled.

## Test Signals
Useful tests cover sorted creation, insert/delete/fetch by index, predecessor/successor searches, split/merge, conversion between array and tree forms, mark iteration/deletion, and memory-size accounting.
