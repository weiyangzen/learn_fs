# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/ft/comparator.h

## Purpose
`comparator.h` wraps a legacy Fractal Tree key comparison callback in `toku::comparator`, adding support for negative and positive infinity DBTs and carrying an optional memcmp magic byte.

## Important APIs, Types, And Functions
`ft_compare_func` is the callback signature `int(void*, const DBT*, const DBT*)`. Free declarations include `toku_keycompare()` and default-visible `toku_builtin_compare_fun()`.

`toku::comparator` exposes `create()`, `inherit()`, `create_from()`, `destroy()`, `get_compare_func()`, `get_memcmp_magic()`, `valid()`, and `operator()(const DBT*, const DBT*)`. `MEMCMP_MAGIC_NONE` disables the magic shortcut.

## Control Flow
`operator()` first routes any infinite endpoint through `toku_dbt_infinite_compare()`. If memcmp magic is configured and both DBTs carry it, the code asserts because this RocksDB port expects not to take that branch, but still contains the legacy built-in compare call. Otherwise it invokes `_cmp(_cmp_arg, a, b)`.

## State And Persistence Behavior
The object stores only the callback pointer, callback argument, and magic byte. It does not own comparator argument memory; callers must ensure the underlying comparator context outlives the locktree.

## Dependencies
It includes DBT compatibility, memory/assert macros, and DBT helper functions from `util/dbt.h`. The actual RocksDB comparator adaptation lives outside this header.

## Integration Points
`keyrange`, `treenode`, `locktree`, and `locktree_manager::get_lt()` depend on this wrapper for every endpoint ordering decision. Range-lock comparator tests specifically protect reverse comparator and timestamp comparator behavior through the adapter using this surface.

## Risks And Edge Cases
Comparator lifetime is external and easy to violate. The memcmp magic branch asserts, so enabling it inadvertently would abort debug builds. Infinite DBTs must be distinguishable by pointer/helper predicates or range ordering breaks.

## Test Signals
`RangeLockWithReverseComparator` and `RangeLockWithTimestampComparator` are the strongest direct signals. Tree insertion, overlap, escalation, and release tests indirectly cover ordinary and infinite endpoint comparisons.
