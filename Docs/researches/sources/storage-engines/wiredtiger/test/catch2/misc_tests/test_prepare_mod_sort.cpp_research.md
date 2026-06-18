# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_prepare_mod_sort.cpp

## Purpose
Tests transaction modification sorting via `__ut_txn_mod_compare`, ensuring operations sort by btree ID, key/recno, and keyedness rules needed for prepared transaction handling.

## Important APIs, Types, And Functions
Helpers include `has_key`, `__mod_ops_sorted`, `rand_non_keyd_type`, `init_btree`, `init_op`, `init_key`, `random_keys`, and `allocate_key_space`. Tests call `__wt_qsort` with `__ut_txn_mod_compare` over arrays of `WT_TXN_OP`.

## Control Flow
Scenarios cover basic column operations with non-keyed ops, row operations with non-keyed ops, mixed row/column/non-keyed ops, btree ID ordering, keyedness ordering, many row-store keys over two btrees, and column-store recno ordering. Tests allocate scratch keys where needed, sort, validate ordering, and free buffers.

## State And Persistence Behavior
All btrees, operations, and keys are in-memory test structures. `connection_wrapper` sessions provide scratch-buffer allocation for row keys.

## Dependencies And Integration Points
Depends on `wiredtiger.h`, `wt_internal.h`, `utils.h`, `item_wrapper`, `connection_wrapper`, and transaction operation internals.

## Risks And Edge Cases
Risks include non-keyed operations disrupting comparisons, row-key lexicographic ordering, column recno ordering, randomized duplicate btree IDs/keys, and comparator behavior across btree types.

## Test Signals
After sorting, `__mod_ops_sorted` must return true for each scenario. Scratch buffers are freed before assertion where needed.
