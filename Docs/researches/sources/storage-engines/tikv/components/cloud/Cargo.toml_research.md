# sources/storage-engines/tikv/components/cloud/Cargo.toml

## Purpose
This manifest defines the workspace `cloud` component, which provides provider-neutral cloud storage and KMS abstractions used by concrete provider crates such as AWS and Azure.

## Important APIs, Types, And Functions
As a Cargo manifest it declares package metadata and dependency surfaces rather than Rust functions. The dependencies indicate that the crate exposes async traits, structured errors, protobuf-backed config integration, futures-based streaming, metrics, URL handling, UUIDs, and TiKV utility integration. Dev dependencies include `pin-project` and a Tokio runtime for tests.

## Control Flow
Cargo uses this file to compile the `cloud` crate with Rust 2021 edition and no publishing. There are no features in this manifest. Downstream crates depend on the traits and error types exported by this crate through workspace dependency wiring.

## State And Persistence Behavior
The manifest has no runtime state. Its dependency set controls what runtime state the library can model: blob config URLs, streaming resources, metrics counters/histograms, protobuf configuration, and KMS error types.

## Dependencies And Integration Points
The most important integration points are `kvproto` for BR/cloud protobuf configuration, `prometheus` for `CLOUD_*` metrics, `tikv_util` for common utilities, `futures`/`futures-io` for async object streams, and `error_code`/`thiserror`/`derive_more` for structured errors. Provider crates import these common traits and types.

## Risks
Because this is the abstraction crate, dependency version or feature changes affect every cloud backend. `prometheus` is built with `nightly`; removing or changing that feature can affect metrics compilation. The crate uses `protobuf` 2.x with bytes support, which must stay compatible with `kvproto`.

## Test Signals
This manifest's direct test signal is compilation of the `cloud` crate and provider crates that depend on it. Dev dependencies suggest unit tests exercise async streams under Tokio.
