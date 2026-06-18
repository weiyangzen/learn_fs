# sources/storage-engines/rocksdb/utilities/merge_operators/sortlist.h

## Purpose
This header declares `SortList`, a `MergeOperator` for merging sorted integer-list operands.

## Important APIs, types, and functions
The class overrides `FullMergeV2`, `PartialMerge`, and `PartialMergeMulti`, exposes `Name()` as `"MergeSortOperator"` and `NickName()` as `"sortlist"`, and provides public `MakeVector()` plus private `Merge()`.

## Control flow
No inline control flow beyond names; implementation is in `sortlist.cc`.

## State and persistence behavior
The operator stores no members and is stateless.

## Dependencies and integration points
It depends on RocksDB merge and slice APIs. It is exposed through `MergeOperators::CreateSortOperator()` and registry string creation.

## Risks and edge cases
The public `MakeVector()` mutates its `Slice` parameter's data pointer copy and assumes input format. The header does not document malformed input behavior or `PartialMergeMulti()` limitations.

## Test signals
No direct tests in this subset.
