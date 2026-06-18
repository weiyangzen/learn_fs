# sources/storage-engines/rocksdb/db_stress_tool/db_stress_wide_merge_operator.cc

## Purpose
`db_stress_wide_merge_operator.cc` implements the wide-column-aware merge operator used by `db_stress` when merge operands need to follow the same value-generation rules as normal writes. It is compiled only with gflags support.

## Important APIs, types, and functions
The single implementation is `DBStressWideMergeOperator::FullMergeV3(const MergeOperationInputV3&, MergeOperationOutputV3*)`. It uses `MergeOperationInputV3::operand_list`, `MergeOperationOutputV3::new_value`, `MergeOperationOutputV3::NewColumns`, `GetValueBase()`, `GenerateWideColumns()`, and the global `FLAGS_use_put_entity_one_in`.

## Control flow
The method asserts non-empty operands and a valid output pointer, selects the last operand as the merge result basis, and rejects operands smaller than a `uint32_t` because they cannot encode a value base. It extracts `value_base` from the latest operand. If wide-entity generation is disabled (`FLAGS_use_put_entity_one_in == 0`) or the value base is not a selected multiple, the output is the raw latest operand. Otherwise it generates wide columns for that value base, switches `new_value` to the `NewColumns` variant, reserves space, and copies each column name/value into owned strings.

## State and persistence behavior
The operator is stateless. It has no persistent data and bases the merge result solely on the current operand list and the process-wide stress flag. Persistence effects happen later in RocksDB when the merged value or entity is materialized.

## Dependencies and integration points
It depends on the declaration in `db_stress_wide_merge_operator.h`, stress helpers in `db_stress_common.h`, and RocksDB's merge operator V3 API. It integrates with the validation logic that expects values derived from merge operands to match `GenerateValue`/wide-column generation behavior.

## Risks and test signals
The important correctness constraint is that the merge result must match the rules used by puts; otherwise validation reads would see a value shape the expected-state logic cannot explain. Returning false for malformed short operands is a corruption signal. Tests should cover raw value output, wide-column output, last-operand-wins semantics, and disabled wide-entity generation.
