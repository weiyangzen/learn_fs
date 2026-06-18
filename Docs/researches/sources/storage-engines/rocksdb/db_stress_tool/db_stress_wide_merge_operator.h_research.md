# sources/storage-engines/rocksdb/db_stress_tool/db_stress_wide_merge_operator.h

## Purpose
`db_stress_wide_merge_operator.h` declares the test merge operator that lets `db_stress` exercise `MergeOperator::FullMergeV3` with both plain values and wide-column entities.

## Important APIs, types, and functions
The key type is `DBStressWideMergeOperator`, derived from `rocksdb::MergeOperator`. It overrides `FullMergeV3()` and `Name()`, returning `"DBStressWideMergeOperator"`. The comments document the essential semantic contract: like put-style merge operators, the result is based on the last merge operand, but may become a wide-column entity depending on the encoded value base and `use_put_entity_one_in`.

## Control flow
The header itself has no runtime control flow. Its declaration selects the V3 merge interface so the `.cc` file can return either a raw value or a wide-column result through the variant output type.

## State and persistence behavior
The class carries no fields. Merge behavior is entirely functional from the input operand list and global stress options, so instances can be shared without per-instance state.

## Dependencies and integration points
It includes `rocksdb/merge_operator.h` and lives in `ROCKSDB_NAMESPACE`. It is consumed by the stress option assembly path when merge testing and wide-column testing intersect. The declared behavior is also coupled to `GenerateWideColumns()` and value-base encoding in `db_stress_common.h`.

## Risks and test signals
Any future change to the expected value encoding or wide-column generation must keep this operator in sync. Because the class uses the V3 API, tests should ensure build configurations with `GFLAGS` still compile and that old merge interfaces are not accidentally selected for wide-column stress.
