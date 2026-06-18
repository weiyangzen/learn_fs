# sources/storage-engines/rocksdb/utilities/merge_operators/string_append/stringappend.h

## Purpose
This header declares `StringAppendOperator`, the production associative merge operator for delimiter-separated string append.

## Important APIs, types, and functions
Constructors accept a delimiter character or string. `Merge()` implements `AssociativeMergeOperator`. `Name()` returns `"StringAppendOperator"` and `NickName()` returns `"stringappend"`. The only data member is `std::string delim_`.

## Control flow
No inline merge logic is defined here; implementation is in `stringappend.cc`.

## State and persistence behavior
The delimiter is stored per operator instance and participates in options serialization through registration in the implementation.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h` and `rocksdb/slice.h`. It is used by `MergeOperators` factories, options parsing, and DB configurations.

## Risks and edge cases
Because delimiter is instance state, opening a DB with a different delimiter changes future merge interpretation. Existing materialized values are plain strings and do not encode delimiter metadata.

## Test signals
Covered by `stringappend_test.cc`.
