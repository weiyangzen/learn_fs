# sources/storage-engines/tikv/components/cloud/aws/src/lib.rs

## Purpose
This is the AWS provider crate root. It wires private implementation modules and re-exports the public AWS KMS and S3 types used by the rest of TiKV.

## Important APIs, Types, And Functions
The crate declares `mod kms`, `mod s3`, and `mod util`. It publicly re-exports `AwsKms` and `ENCRYPTION_VENDOR_NAME_AWS_KMS` from `kms`, and `Config`, `S3Storage`, `STORAGE_NAME`, and `STORAGE_VENDOR_NAME_AWS` from `s3`. `util` remains private implementation support.

## Control Flow
There is no runtime control flow in this file. Rust module loading compiles the three modules, and downstream code imports the re-exported provider types from the crate root.

## State And Persistence Behavior
The file has no state. Its re-export decisions define the external API boundary: callers can construct S3 storage and KMS providers but cannot directly access HTTP/credential helper functions.

## Dependencies And Integration Points
`lib.rs` is the integration point between the AWS crate and workspace consumers. It keeps the AWS utility module private while exposing only provider implementations and provider/vendor names.

## Risks
Changing re-exports is a semver-like workspace API change even though the crate is unpublished. Hiding `util` means tests or other crates must use public constructors rather than shared helpers unless they are inside this crate.

## Test Signals
The crate-root behavior is tested indirectly by compiling downstream imports and the unit tests in `kms.rs`, `s3.rs`, and `util.rs`.
