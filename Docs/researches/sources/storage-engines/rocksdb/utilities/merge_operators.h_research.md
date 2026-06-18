# sources/storage-engines/rocksdb/utilities/merge_operators.h

## Purpose
This header declares the `MergeOperators` factory convenience class for constructing RocksDB built-in merge operators.

## Important APIs, types, and functions
Factory methods include `CreatePutOperator`, `CreateDeprecatedPutOperator`, `CreateUInt64AddOperator`, `CreateStringAppendOperator()` overloads, `CreateStringAppendTESTOperator`, `CreateMaxOperator`, `CreateBytesXOROperator`, `CreateSortOperator`, and `CreateFromStringId`.

## Control flow
The header only declares static methods. Implementations in operator-specific `.cc` files return `shared_ptr<MergeOperator>` for concrete operators, while `merge_operators.cc` implements string-id lookup.

## State and persistence behavior
No state is declared in this header. Returned operators are owned by `shared_ptr`s.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h` and standard string/memory headers. It is the public utility entry point used by applications, tests, and options parsing to obtain built-in merge operators.

## Risks and edge cases
The class mixes stable production operators with test/deprecated operators, so callers must choose intentionally. `CreateFromStringId()` may return null rather than surfacing a detailed `Status`.

## Test signals
Coverage comes from individual merge operator tests and options/object-registry tests that create operators from names.
