# sources/storage-engines/tikv/src/coprocessor/error.rs

Purpose: defines the coprocessor error model and conversions from lower storage/query layers. `Error` distinguishes retryable region errors, lock conflicts, deadline, admission, memory quota, max-ts update, default-CF missing values, and generic other errors.

Important APIs: `Result<T>` aliases `std::result::Result<T, Error>`. `From` implementations convert boxed errors, query `StorageError`/`EvaluateError`, `tidb_query_common::Error`, KV/MVCC/txn errors, deadline errors, datatype/codec errors, and `MemoryQuotaExceeded`. `ErrorCodeExt::error_code` maps variants to TiKV error codes.

Control flow: lower-level errors are collapsed into response-relevant categories. Region and lock errors preserve structured protobuf details; default-not-found is separated for logging/response treatment; unknowns become `Other`. `From<StorageError>` attempts to downcast back to coprocessor `Error`.

State/persistence: none. Dependencies are TiKV storage error types, `kvproto`, `error_code`, `thiserror`, and memory quota. Integration points are endpoint response formatting, DAG storage error conversion, and query engine storage bridges. Risks are lossy conversion into `Other`, downcast failure text hiding original structure, and ensuring newly introduced storage errors receive appropriate structured mappings. No local tests; endpoint tests validate several response conversions.
