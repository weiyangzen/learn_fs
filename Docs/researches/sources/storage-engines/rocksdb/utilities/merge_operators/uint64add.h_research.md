# sources/storage-engines/rocksdb/utilities/merge_operators/uint64add.h

## Purpose
This header declares `UInt64AddOperator`, a model associative merge operator for uint64 addition.

## Important APIs, types, and functions
The class exposes class name `"UInt64AddOperator"`, nickname `"uint64add"`, overrides `Merge()`, and has private helper `DecodeInteger()`.

## Control flow
No inline behavior beyond names; implementation is in `uint64add.cc`.

## State and persistence behavior
No state is stored.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h` and `utilities/merge_operators.h`. It is available through factory helpers and object registry lookup.

## Risks and edge cases
The header does not communicate overflow or corrupt-input-as-zero semantics; callers must consult implementation or docs.

## Test signals
No direct test in this subset.
