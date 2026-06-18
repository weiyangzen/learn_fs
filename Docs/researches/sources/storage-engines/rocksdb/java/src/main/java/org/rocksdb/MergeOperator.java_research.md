# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MergeOperator.java research

## Purpose

`MergeOperator` is the abstract Java base for native RocksDB merge operators. It represents a native operator that combines merge operands for a key during reads or compaction.

## Important APIs and types

The only constructor is protected and accepts a native handle, passing it to `RocksObject`. Concrete subclasses provide actual operators, typically by creating named or native merge-operator handles.

## Control flow

Subclasses construct native merge operators and call this constructor. `Options.setMergeOperator(MergeOperator)` passes the stored native handle to native options.

## State and persistence behavior

The class owns a native merge operator handle through `RocksObject`. Merge operators affect logical value computation and compaction output, which can become durable in SST files after compaction or flush.

## Dependencies and integration points

It integrates with `Options`, column-family options, read paths, write paths using merge operands, and native compaction.

## Risks and test signals

Risks are lifecycle misuse and operator/DB incompatibility when reopening without the same operator. Tests should verify installation, merge semantics across get/compaction/reopen, and proper close behavior for concrete operators.
