# sources/storage-engines/rocksdb/utilities/merge_operators/put.cc

## Purpose
This file implements merge operators that mimic Put semantics by making the latest merge operand become the value.

## Important APIs, types, and functions
`PutOperator::FullMerge()` assigns `operand_sequence.back()` to `new_value`. `PartialMerge()` assigns the right operand. `PartialMergeMulti()` assigns the last operand.

`PutOperatorV2::FullMerge()` is intentionally disabled with `assert(false)` and returns false; `FullMergeV2()` writes the last operand to `merge_out->existing_operand`.

`MergeOperators::CreateDeprecatedPutOperator()` returns `PutOperator`; `CreatePutOperator()` returns `PutOperatorV2`.

## Control flow
Every active merge path chooses the newest/rightmost operand and ignores existing value. This makes merge accumulation equivalent to overwriting with the latest value.

## State and persistence behavior
The operators are stateless. Persistent DB values become the latest merge operand after reads or compactions resolve merge operands.

## Dependencies and integration points
It depends on RocksDB merge/slice APIs and `utilities/merge_operators.h`. `PutOperatorV2` is registered as nickname `"put"` while deprecated v1 uses `"put_v1"`.

## Risks and edge cases
The code asserts non-empty operand sequences but does not handle empty input gracefully in release builds. `PutOperatorV2::FullMerge()` must not be called by code paths expecting only legacy full-merge API. This operator is primarily for testing and examples, not production.

## Test signals
No direct test in this subset; behavior is likely covered by merge operator tests elsewhere.
