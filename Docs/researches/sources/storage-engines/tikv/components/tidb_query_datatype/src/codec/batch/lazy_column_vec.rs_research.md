# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/lazy_column_vec.rs

## Purpose
Stores a batch of equal-length lazy columns plus optional common-handle keys exchanged between executors.

## APIs, Flow, And State
`LazyBatchColumnVec` wraps `Vec<LazyBatchColumn>` and `Option<Vec<Vec<u8>>>` for `extra_common_handle_keys`. It constructs from lazy columns or decoded `VectorValue`s, clones empty columns with preserved schema, exposes column and row counts, push/swap-remove adapters, equal-length assertion, maximum encoded-size estimates, row-wise binary encoding, and column-wise chunk encoding. It can truncate all columns to the shortest length and offers slice/index access for single and range indexing. Extra common handle keys are lazily allocated, queried, retrieved by row, or taken.

## Dependencies And Integration
Depends on `LazyBatchColumn`, `VectorValue`, `FieldType`, `EvalContext`, and codec `Result`. Batch executors use it as the shared row-batch container between scans, selections, expressions, and output encoders.

## Risks And Test Signals
The struct assumes equal column lengths but only enforces that when callers invoke `assert_columns_equal_length` or `truncate_into_equal_length`. Output offsets and schema indexes must align. Extra handle keys are not automatically length-checked against rows. Coverage is mostly through users and lazy column tests rather than direct tests in this file.
