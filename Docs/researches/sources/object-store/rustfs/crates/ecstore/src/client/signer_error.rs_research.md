# sources/object-store/rustfs/crates/ecstore/src/client/signer_error.rs

## Purpose
Normalizes signer failures into IO errors while preserving invalid UTF-8 header names for detection by higher layers/tests.

## Important APIs, types, and functions
`SIGNER_HEADER_ERROR_MARKER` is an internal marker string. `invalid_utf8_header_error`, `signer_error_to_io_error`, and `error_chain_contains_signer_header_marker` are crate-visible helpers. `SignerHeaderError` is a private error type carrying scope and header name.

## Control flow
Invalid signer header values are converted into `ErrorKind::InvalidInput` with a structured source error. Other signer errors become generic `Error::other` messages. Detection walks an error chain, checks for `SignerHeaderError` by downcast, and falls back to marker-string matching.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
The module is used by transition request signing and bucket-location signing. It depends on `rustfs_signer::SignV4Error` and standard error chaining.

## Risks and edge cases
Marker-string fallback is intentionally redundant but means unrelated errors containing the marker text can be classified as signer header errors. Non-header signing errors lose structured type information when converted to string IO errors.

## Test signals
Unit tests verify direct invalid UTF-8 header errors and mapped signer header errors are detectable through the error chain, while unrelated IO errors are not.
