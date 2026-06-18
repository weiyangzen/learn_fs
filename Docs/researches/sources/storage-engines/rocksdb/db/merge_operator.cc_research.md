# sources/storage-engines/rocksdb/db/merge_operator.cc

## Purpose
`merge_operator.cc` provides default backend implementations for RocksDB merge operator API evolution. It adapts older `FullMerge`/`FullMergeV2` operators to `FullMergeV3`, implements default multi-operand partial merging through pairwise `PartialMerge`, and implements associative merge behavior in terms of a simpler `Merge` callback.

## Important APIs, types, and functions
`MergeOperator::FullMergeV2` is the compatibility fallback for operators that only implement legacy `FullMerge`. It copies the `Slice` operand list into `std::deque<std::string>` and calls `FullMerge`.

`MergeOperator::FullMergeV3` adapts V3 inputs with variant existing values. For no base or plain base, it delegates to `FullMergeV2`. For wide-column existing values, it extracts the default column as the V2 base value if present, calls `FullMergeV2`, and then rebuilds a V3 `NewColumns` output preserving non-default columns.

`MergeOperator::PartialMergeMulti` loops over operands and invokes `PartialMerge` pairwise, carrying the latest merged result as the next left operand.

`AssociativeMergeOperator::FullMergeV2` repeatedly calls the user's associative `Merge` function over the existing value and each operand. `AssociativeMergeOperator::PartialMerge` calls `Merge` with the left operand as the existing value.

## Control flow
The compatibility flow always moves from newer API shape to older override when a user operator has not supplied a newer implementation. V3 creates a V2 input/output pair, invokes `FullMergeV2`, propagates failure scope on failure, then maps either `new_value` or `existing_operand` back into the V3 output variant.

For wide columns, only the default column participates in legacy merge semantics. The fallback then emits a new default-column value plus all existing non-default columns. If no default column existed, it adds one before copying existing columns.

Partial merge multi starts from operand zero, merges it with each subsequent operand, swaps the temporary result into `new_value`, and updates the temporary slice to point at the accumulated result. Associative full merge is similar but starts from the optional existing base value and invokes the user's associative `Merge` for each operand.

## State and persistence behavior
This file has no persistent state. It defines semantic defaults that directly affect read and compaction results, which later become persisted values when compaction writes merged output. The wide-column fallback preserves non-default columns by copying names and values into the V3 output.

## Dependencies and integration points
The implementation depends on the public `rocksdb/merge_operator.h`, wide column helper utilities, and a variant `overload` helper. It is used by `MergeHelper::TimedFullMerge`, memtable point lookups, DB reads, and compaction whenever a merge operator does not override the latest API.

## Risks and edge cases
The compatibility path copies operands into strings for legacy `FullMerge`, which can be expensive. Wide-column fallback only gives legacy operators the default column; operators unaware of wide columns cannot inspect or modify non-default columns except through preservation. `PartialMergeMulti` assumes at least two operands and returns false on the first pairwise failure. Returned `existing_operand` slices must point to still-valid operand storage.

## Test signals
`merge_test.cc` directly tests V3 fallback for string new values, returned operand slices, wide-column bases with and without default columns, and failure-scope propagation. DB-level merge tests exercise associative full and partial merge fallbacks through `CountMergeOperator`.
