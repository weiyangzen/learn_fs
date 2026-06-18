# sources/object-store/rustfs/crates/trusted-proxies/src/cloud/metadata/mod.rs

Purpose: Metadata provider module aggregator for cloud-specific trusted proxy discovery.

Important APIs: Declares private submodules `aws`, `azure`, and `gcp`, then publicly re-exports each module's contents with `pub use`. No local functions or state.

Control flow and state: Compile-time module wiring only. It creates the public namespace where fetchers such as `AwsMetadataFetcher`, `AzureMetadataFetcher`, and `GcpMetadataFetcher` become visible to the rest of the crate.

Dependencies and integration: Sits under `cloud/mod.rs` and feeds the crate-level re-exports in `lib.rs`. Consumers can import provider fetchers from `rustfs_trusted_proxies::*` without knowing the file layout.

Risks and tests: Risk is mainly namespace coupling: adding a provider here changes the public API. Integration tests import `AwsMetadataFetcher` through the public path, indirectly confirming these re-exports compile.
