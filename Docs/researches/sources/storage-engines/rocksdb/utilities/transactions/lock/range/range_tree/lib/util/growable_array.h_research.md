# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/growable_array.h

## Purpose
Defines a minimal constructor-free dynamic array used by imported Toku structures, especially temporary index lists in OMT mark deletion.

## Important APIs, Types, And Functions
`toku::GrowableArray<T>` exposes `init`, `deinit`, `fetch_unchecked`, `store_unchecked`, `push`, `get_size`, and `memory_size`.

## Control Flow
`init` zeroes the pointer and sizes. `push` doubles capacity when full, using `XREALLOC_N`, then stores the new value. `deinit` frees the backing array. Fetch/store are unchecked except for a paranoid invariant in store.

## State And Persistence Behavior
State is a heap buffer, element count, and capacity. Nothing persists. Elements are copied by assignment and no element destructors are run explicitly.

## Dependencies And Integration Points
Uses Toku allocation wrappers and invariant macros from portability headers. OMT uses it to collect marked indexes before deleting them.

## Risks And Edge Cases
The class is only safe for trivially managed values; it does not construct or destroy elements like `std::vector`. `fetch_unchecked` has no bounds check. Callers must remember `init` and `deinit`.

## Test Signals
Indirect OMT mark deletion tests exercise growth and cleanup. Memory instrumentation can detect forgotten `deinit` calls or unsafe element types.
