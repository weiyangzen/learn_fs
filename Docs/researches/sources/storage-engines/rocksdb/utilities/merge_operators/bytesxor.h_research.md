# sources/storage-engines/rocksdb/utilities/merge_operators/bytesxor.h

## Purpose
This header declares `BytesXOROperator`, a model `AssociativeMergeOperator` for byte-wise XOR semantics.

## Important APIs, types, and functions
The class overrides `Merge()`, exposes `Name()` as `"BytesXOR"`, `NickName()` as `"bytesxor"`, and provides public helper `XOR(const Slice*, const Slice&, std::string*)`.

## Control flow
The header defines no inline control flow beyond names. Implemented behavior is in `bytesxor.cc`.

## State and persistence behavior
The operator stores no member state.

## Dependencies and integration points
It includes RocksDB env, merge operator, slice, coding utilities, and `utilities/merge_operators.h`. It participates in `MergeOperators::CreateBytesXOROperator()` and object-registry registration.

## Risks and edge cases
The exposed `XOR()` helper lets tests or callers use the byte logic outside a merge operation, but it inherits the same no-validation behavior.

## Test signals
No direct tests in this subset.
