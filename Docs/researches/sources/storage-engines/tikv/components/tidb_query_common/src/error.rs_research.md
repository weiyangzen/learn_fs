# sources/storage-engines/tikv/components/tidb_query_common/src/error.rs

Purpose: defines the common error model for query evaluation and storage access. It separates evaluation failures from storage failures while presenting a single `tidb_query_common::Result`.

Important APIs and control flow: `EvaluateError` contains deadline, invalid charset, custom codec-compatible, and generic variants, with MySQL/TiDB-style numeric `code()`. It implements conversions from boxed errors, deadline errors, UTF-8/JSON errors, and `Infallible`. `StorageError` wraps `anyhow::Error`; `ErrorInner` distinguishes storage and evaluate sources; `Error` boxes `ErrorInner`. A default generic `From<T: Into<EvaluateError>> for Error` maps convertible failures to evaluation errors.

State and persistence behavior: stateless error values only. Error codes are computed from variants and integrated with `error_code::ErrorCodeExt`.

Dependencies and integration: used throughout aggregate, expression, and storage scanner code as `Result<T>`. `other_err!` constructs `EvaluateError::Other` values through this module.

Risks and test signals: generic specialization for `From<T>` relies on nightly min specialization and can overlap if new conversions are added. `EvaluateError::Custom` is a compatibility layer, so richer error typing may be hidden. Tests are indirect through consumers that assert failures or error codes.
