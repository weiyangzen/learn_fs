# sources/storage-engines/tikv/components/cloud/azure/Cargo.toml

## Purpose
This manifest defines the TiKV Azure cloud provider crate. It supplies Azure Blob Storage and Azure Key Vault support over the shared `cloud` crate abstractions.

## Important APIs, Types, And Functions
As a manifest, it declares dependencies rather than code APIs. The dependency set shows the crate uses Azure SDK crates (`azure_core`, `azure_identity`, `azure_security_keyvault`, `azure_storage`, `azure_storage_blobs`), shared `cloud` types, `kvproto` config, async traits and futures, OAuth2, OpenSSL-backed HMAC, serde/JSON, TiKV logging/utilities, Tokio time, URL parsing, and UUID v4.

## Control Flow
Cargo compiles this non-published Rust 2021 workspace package with the selected Azure SDK crates and disabled default features on several Azure packages. There are no features declared in this manifest.

## State And Persistence Behavior
The manifest has no runtime state. It enables runtime behaviors implemented elsewhere in the Azure crate: token/identity handling, Key Vault calls, blob operations, signed storage requests, JSON parsing, and time-aware credential handling.

## Dependencies And Integration Points
The crate integrates the shared `cloud` abstraction layer with Azure SDKs, `kvproto`, TiKV logging/util, OpenSSL, OAuth2, and Tokio. `azure_core` is built with `hmac_openssl`, so OpenSSL is part of the request signing path.

## Risks
The Azure SDK versions are all `0.18`, so updating one package likely requires updating the family together. Default features are disabled for several SDK crates, which keeps builds smaller but can surprise new code that expects default transports or crypto. UUID is version `1.0` here while the root cloud crate uses `0.8`, so cross-crate UUID types should not be shared directly.

## Test Signals
Compilation of the Azure crate validates dependency compatibility. Runtime tests live in the Azure source files rather than this manifest; this manifest's signal is that Azure storage/KMS code can resolve the required SDK, crypto, logging, and async dependencies.
