# sources/storage-engines/rocksdb/utilities/merge_operators/sortlist.cc

## Purpose
This file implements `SortList`, a merge operator that takes operands representing comma-separated sorted integer lists and merges them into one sorted comma-separated list.

## Important APIs, types, and functions
`FullMergeV2()` iterates through `merge_in.operand_list`, parses each operand with `MakeVector()`, merges it into an accumulated vector using `Merge()`, and serializes the result to `merge_out->new_value`.

`PartialMerge()` parses left and right operands, merges them, and serializes to `new_value`.

`PartialMergeMulti()` currently ignores inputs and returns true without writing a value.

`MakeVector()` parses integers separated by commas using `std::stoi`. `Merge()` performs the standard two-pointer merge of sorted vectors. `MergeOperators::CreateSortOperator()` returns a shared `SortList`.

## Control flow
Both active merge paths parse string operands into vectors, merge sorted inputs pairwise, then append values with commas between all but the last. `Merge()` preserves duplicates.

## State and persistence behavior
The operator is stateless. DB values persist as serialized sorted integer lists after merge resolution.

## Dependencies and integration points
It depends on `sortlist.h`, RocksDB merge/slice APIs, and the merge operator factory header. It is registered under `"MergeSortOperator"` and `"sortlist"`.

## Risks and edge cases
`FullMergeV2()` and `PartialMerge()` call `left.back()` or serialize assuming non-empty lists; empty operands or no operands can crash or produce undefined behavior. `MakeVector()` directly advances `Slice::data_`, depends on null/comma termination behavior, and can throw from `std::stoi` on invalid integers. `PartialMergeMulti()` returning true without output is suspicious and could lose data if used by merge scheduling.

## Test signals
No direct test in this subset. This operator needs focused tests for empty operands, malformed integers, multi-operand partial merge, duplicates, and negative numbers.
