# Research: sources/storage-engines/rocksdb/include/rocksdb/merge_operator.h

## Purpose

`merge_operator.h` declares the application-defined semantics for RocksDB merge operands. It lets RocksDB store incremental updates and later combine them during reads, iteration, flush, or compaction using client-supplied logic.

## Important APIs, Types, and Functions

`MergeOperator` extends `Customizable` and exposes deprecated `FullMerge`, `FullMergeV2`, wide-column-capable `FullMergeV3`, `PartialMerge`, `PartialMergeMulti`, `Name`, `AllowSingleOperand`, `ShouldMerge`, and `CreateFromString`. Input/output structs include `MergeOperationInput`, `MergeOperationOutput`, `MergeOperationInputV3`, and `MergeOperationOutputV3`. `OpFailureScope` lets failed merges distinguish try-merge failures from must-merge failures. `AssociativeMergeOperator` provides a simpler `Merge` method and implements the generic methods in terms of associative pairwise merging.

## Control Flow

Write operations can append merge operands without reading the old value. Later, RocksDB calls full merge when a base value or deletion boundary is available, or calls partial merge to collapse operands before a base value is known. During `Get`, RocksDB can call `ShouldMerge` to decide whether to force a full merge after seeing a reversed operand stack. During compaction, failed try-merge can make background work fail, while must-merge failures can allow compaction to keep original operands.

## State and Persistence Behavior

Merge operands are persisted in memtables, WALs, and SSTs as merge records until collapsed. The operator object itself is not persisted in this header; `Name()` is intended for mismatch checking, but the comment notes the name is not persistently enforced and clients must reopen with consistent semantics. V3 supports plain values, no value, and wide-column entities as merge bases and outputs.

## Dependencies and Integration Points

The header depends on `Customizable`, `Slice`, and `wide_columns.h`. Implementations and built-ins are registered in `utilities/merge_operators.cc`, including string append, uint64 add, bytesxor, max, sortlist, and put variants. Integration points include `table/get_context.cc`, table properties, options parsing, Java/JNI merge operators, TTL wrapping merge operator, transaction tests, and SST file writer/reader tests.

## Risks and Edge Cases

Exceptions must not propagate into RocksDB. Merge semantics must be deterministic and stable across DB reopen, backup, compaction, and language bindings. Returning false has serious consequences: reads can fail and flush/compaction can put the DB in read-only mode depending on `OpFailureScope`. Partial merges must preserve exact sequential semantics. The operand order differs for `ShouldMerge`, which receives reversed order for performance. Wide-column fallback in `FullMergeV3` can preserve non-default columns while merging only the default column, which custom operators must understand.

## Test Signals

Signals include options tests for `MergeOperator::CreateFromString`, table and SST reader tests using string append and uint64 add, transaction merge tests, TTL merge operator tests, Java merge operator tests, and get-context handling of `kMergeOperatorFailed`. Good tests cover full merge with/without base value, partial merge equivalence, false-return scopes, reopen with matching operator, wide-column merge behavior, and compaction/read differences.
