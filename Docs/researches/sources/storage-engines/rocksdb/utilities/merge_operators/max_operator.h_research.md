# sources/storage-engines/rocksdb/utilities/merge_operators/max_operator.h

## Purpose
This header declares `MaxOperator`, a `MergeOperator` that selects the maximum operand by `Slice::compare()`.

## Important APIs, types, and functions
It exposes `kClassName()` as `"MaxOperator"`, `kNickName()` as `"max"`, overrides `Name()`, `NickName()`, `FullMergeV2()`, `PartialMerge()`, and `PartialMergeMulti()`.

## Control flow
No inline logic beyond names; implementation is in `max.cc`.

## State and persistence behavior
The class has no data members and is stateless.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h` and forward declares `Logger` and `Slice`. It is consumed by merge operator factories and registry registration.

## Risks and edge cases
The header documents only "maximum operand"; callers must know that maximum is lexicographic `Slice` comparison.

## Test signals
No direct test in this subset.
