# sources/storage-engines/tikv/components/encryption/src/errors.rs

Purpose: Defines the encryption crate's central `Error` enum, `Result<T>` alias, retry-code plumbing, and adapters for cloud KMS errors. It is the boundary type used by dictionary persistence, master-key backends, stream crypters, and RocksDB integration.

Important APIs and types: `Error` wraps boxed generic errors, recoverable tail-record parse failures, retry-coded KMS errors, RocksDB strings, IO, OpenSSL, protobuf, wrong-master-key, and both-master-key-failed cases. `RetryCodedError` composes `Debug`, `Display`, `ErrorCodeExt`, `RetryError`, `Send`, and `Sync`. `CloudConvertError` adapts `cloud::error::Error` plus context text into `Error::RetryCodedError`. `cloud_convert_error` returns a closure suitable for `map_err`.

Control flow and state: Error conversion is mostly one-way into `Error`; `From<Error> for IoError` preserves raw IO errors and stringifies all other variants. `ErrorCodeExt` maps variants to TiKV error-code domains, while `RetryError` marks wrong-master-key and both-master-key-failed as non-retryable and currently treats most other cases as retryable.

Dependencies and integration: Used by KMS retry paths, file dictionary recovery, encrypted file parsing, data-key manager load fallback, and external stream retry machinery. It depends on `cloud`, `error_code`, OpenSSL, protobuf, and `tikv_util::stream::RetryError`.

Risks: Retry classification is intentionally broad and may retry protobuf/crypter/corruption errors that are not transient. `Other` maps to generic unknown code, so callers lose detailed classification unless they use specialized variants. `CloudConvertError` stores context separately from the cloud error but preserves the cloud error code and retryability.

Test signals: No local unit tests in this file; behavior is exercised indirectly by master-key backend, KMS, dictionary recovery, and manager tests that match `WrongMasterKey`, `BothMasterKeyFail`, and tail corruption behavior.
