# sources/storage-engines/tikv/components/tidb_query_common/src/macros.rs

Purpose: defines the `other_err!` macro used to construct location-tagged evaluation errors.

Important APIs and control flow: `other_err!($msg)` and `other_err!($fmt, args...)` expand to `tidb_query_common::error::Error::from(EvaluateError::Other(format!(...)))`, prefixing messages with `file!()` and `line!()`.

State and persistence behavior: no state. It creates formatted error values at call sites.

Dependencies and integration: imported with `#[macro_use]` from `tidb_query_common`; aggregate parsers and other query modules use it for unsupported or mismatched request errors.

Risks and test signals: macro pattern only accepts a token-tree first argument and one-or-more format args for the formatted variant, so unusual `format!` forms may not match. File/line inclusion aids diagnostics but can make exact error-string assertions brittle.
