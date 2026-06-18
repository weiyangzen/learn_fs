# sources/storage-engines/rocksdb/utilities/merge_operators/put_operator.h

## Purpose
This header declares the deprecated and V2 Put-like merge operators.

## Important APIs, types, and functions
`PutOperator` exposes class name `"PutOperator"` and nickname `"put_v1"`, overriding legacy `FullMerge`, `PartialMerge`, and `PartialMergeMulti`.

`PutOperatorV2` derives from `PutOperator`, changes nickname to `"put"`, overrides legacy `FullMerge` as unsupported, and implements `FullMergeV2`.

## Control flow
The header declares the split between legacy and V2 merge APIs. Actual newest-operand selection is implemented in `put.cc`.

## State and persistence behavior
No state is stored.

## Dependencies and integration points
It depends on `rocksdb/merge_operator.h`. It is used by factory helpers and object registry registration.

## Risks and edge cases
Inheritance means `PutOperatorV2` still inherits `PartialMerge` behavior from `PutOperator`; callers must not assume all legacy APIs are valid because only `FullMerge` is deliberately disabled.

## Test signals
No direct test in this subset.
