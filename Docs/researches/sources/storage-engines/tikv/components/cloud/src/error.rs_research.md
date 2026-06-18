# sources/storage-engines/tikv/components/cloud/src/error.rs

## Purpose
Defines shared cloud error types, error codes, and retry classification. It gives provider crates a common way to report IO/protobuf/API/KMS errors to TiKV retry and diagnostics layers.

## Important APIs, Types, And Functions
- `Result<T>` aliases `std::result::Result<T, Error>`.
- `ErrorTrait` combines debug/display/error-code/retry/send/sync bounds.
- `Error` variants cover `Other`, `Io`, `Proto`, API timeout/internal/not-found/authentication, and `KmsError`.
- `KmsError` distinguishes `WrongMasterKey`, `EmptyKey`, and `Other`.
- `OtherError` stores a boxed error plus retryable flag.
- `ErrorCodeExt` maps errors into `error_code::cloud::*`.
- `RetryError` implementations classify retryable cloud and KMS errors.

## Control Flow
Provider-specific errors are converted into `OtherError` or `KmsError` and then into `Error`. `From<Error> for IoError` preserves raw IO errors and stringifies all others. Retry logic calls `is_retryable`; most generic cloud errors are retryable except not-found/authentication and wrong/empty KMS keys.

## State And Persistence Behavior
No persistent state. `OtherError` captures the retryability decision at conversion time.

## Dependencies And Integration Points
Integrates `thiserror`, `error_code`, `protobuf::ProtobufError`, and `tikv_util::stream::RetryError`. Used across cloud blob and KMS providers.

## Risks And Edge Cases
`Error::Other` is broadly retryable, but `OtherError::from_box` creates non-retryable `KmsError::Other` when providers do not preserve a `RetryError` implementation. `From<Error> for IoError` loses structured error codes. KMS auth errors must be mapped to `WrongMasterKey` by providers or they can become unknown `Other` errors.

## Test Signals
No direct tests. Coverage is indirect through KMS provider tests asserting `WrongMasterKey` mapping and retry-aware custom errors.
