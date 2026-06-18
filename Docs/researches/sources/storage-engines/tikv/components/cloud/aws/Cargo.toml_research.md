# sources/storage-engines/tikv/components/cloud/aws/Cargo.toml

## Purpose
This manifest defines the TiKV AWS cloud provider crate. It implements S3 blob storage and AWS KMS support on top of the shared `cloud` abstractions.

## Important APIs, Types, And Functions
The manifest exposes one feature, `failpoints`, which enables the `fail/failpoints` dependency path used by AWS credential and S3 timeout/error tests. It pins AWS SDK crates: `aws-config = 1.8.15`, `aws-sdk-kms = 1.103.0`, and `aws-sdk-s3 = 1.126.0`, with default features disabled and selected runtime/client features. The dependency list also includes Smithy runtime crates, static credential support, Hyper/TLS transport, `cloud`, `kvproto`, metrics, logging, Tokio time, UUIDs, MD5, and futures adapters.

## Control Flow
Cargo resolves this crate as a non-published Rust 2021 workspace package. The pinned AWS SDK versions intentionally freeze transitive behavior. Tests add Smithy test utilities, HTTP body support, Tokio macros, and base64/futures utilities.

## State And Persistence Behavior
The manifest has no runtime state. It determines the available runtime capabilities of the AWS implementation: HTTPS client construction, default credential chain, hardcoded credentials, STS assume-role, KMS client, S3 multipart/object operations, MD5 checksums for object lock, and failpoint injection in tests.

## Dependencies And Integration Points
The crate integrates with the shared `cloud` crate, AWS SDK/Smithy stack, TiKV logging and metrics, `kvproto::brpb::S3` configuration, and Hyper 0.14. The `grpcio` dependency is explicitly retained to vendor/link OpenSSL consistently with TiKV's build environment even though it is not part of AWS logic.

## Risks
The AWS SDK family is pinned because unbounded transitive updates have historically changed behavior. Default features are disabled, so adding new AWS SDK usage may require explicit features. Transport versions are tied to Hyper 0.14 and Smithy connector features. The `failpoints` feature changes test behavior and should not leak into normal builds.

## Test Signals
The manifest supports unit tests in `kms.rs`, `s3.rs`, and `util.rs`, including Smithy static replay tests and failpoint-driven credential/S3 timeout tests. Successful `cargo test -p aws` validates both dependency resolution and mocked AWS protocol requests.
