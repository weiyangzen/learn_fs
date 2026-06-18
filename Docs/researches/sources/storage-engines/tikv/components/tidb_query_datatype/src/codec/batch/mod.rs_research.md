# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/mod.rs

## Purpose
Defines the public batch codec module surface for lazy batch column containers.

## APIs, Flow, And State
The module declares `lazy_column` and `lazy_column_vec`, then re-exports `LazyBatchColumn` and `LazyBatchColumnVec`. It has no runtime control flow or persistence.

## Dependencies And Integration
Acts as the import boundary for batch executors and query code that need lazy column storage without referencing internal file names.

## Risks And Test Signals
Risk is limited to accidental API exposure changes. Compilation of downstream batch executor code is the main signal.
