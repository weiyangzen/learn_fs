<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/errors.rs -->
# sources/object-store/rustfs/crates/rio/src/errors.rs

## Purpose
Defines strongly typed validation errors used by the `rio` readers when request bodies, object checksums, SHA-256 values, and declared sizes do not match observed stream data.

## Important APIs, types, and functions
- `Sha256Mismatch`, `BadDigest`, `ChecksumMismatch`, and `InvalidChecksum` represent integrity failures.
- `SizeTooSmall`, `SizeTooLarge`, `SizeMismatch`, and `IncompleteBody` represent body length failures.
- `is_checksum_mismatch` lets higher layers detect a `ChecksumMismatch` through a dynamic error reference.

## Control flow
The file contains no runtime state machine. Its structs are constructed by readers such as `HardLimitReader` and `HashReader`, then carried inside `std::io::Error` or exposed directly as error sources. `is_checksum_mismatch` performs a single `downcast_ref` check.

## State and persistence behavior
There is no persistence. Error structs store expected and observed values as strings or `i64` counts so API layers can map internal validation failures to S3-compatible responses and diagnostics.

## Dependencies and integration points
Depends on `thiserror::Error`. `HashReader` uses `ChecksumMismatch` for content checksum mismatches, while `HardLimitReader` embeds `IncompleteBody` when EOF arrives before the declared content length. API code can use these types to map to S3 errors such as BadDigest or incomplete body.

## Risks and edge cases
Several similarly named size errors exist; callers need to preserve the correct one to avoid ambiguous client responses. `is_checksum_mismatch` only detects a direct `ChecksumMismatch`, not one nested under multiple error wrappers unless the caller unwraps sources.

## Test signals
This file has no local tests. Indirect coverage comes from `HashReader` checksum tests and `HardLimitReader` incomplete-body tests that assert specific error kinds and downcastable markers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/errors.rs -->
