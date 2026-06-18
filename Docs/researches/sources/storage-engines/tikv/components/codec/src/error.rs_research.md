# sources/storage-engines/tikv/components/codec/src/error.rs

## Purpose
Defines the codec crate error model, result alias, compact error boxing, and integration with TiKV error-code reporting.

## APIs and control flow
`ErrorInner` carries concrete failure categories: `Io(io::Error)`, `BadPadding`, and `KeyNotFound`. Helpers `eof` and `bad_padding` construct common errors used by byte and number decoders. Public `Error` wraps `Box<ErrorInner>` and is transparent for formatting. A direct `From<ErrorInner>` and a specialization-based blanket `From<T: Into<ErrorInner>>` convert lower-level errors into boxed `Error`. `Result<T>` aliases `std::result::Result<T, Error>`.

## State, dependencies, and integration
Errors are value objects with no persistent state. The module depends on `thiserror`, `error_code`, `static_assertions`, and `std::io`. `ErrorCodeExt` maps codec failures to `error_code::codec::{IO,BAD_PADDING,KEY_NOT_FOUND}` so upstream TiKV components can classify failures uniformly.

## Risks and test signals
The crate relies on nightly `min_specialization` for the blanket conversion. `const_assert!(8 == size_of::<Result<()>>())` protects the intended small result layout. There are no local unit tests in this file; behavior is exercised indirectly by decode tests that expect EOF, bad padding, and IO propagation.
