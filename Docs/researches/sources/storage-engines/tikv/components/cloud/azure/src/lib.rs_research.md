# sources/storage-engines/tikv/components/cloud/azure/src/lib.rs

## Purpose
Defines the Azure cloud provider crate boundary. It wires internal blob, KMS, and token-credential modules and re-exports the public provider types used by the rest of TiKV.

## Important APIs, Types, And Functions
- `pub use azblob::{AzureStorage, Config}` exposes the Azure Blob implementation and config type.
- `pub use kms::AzureKms` exposes the Azure KMS provider.
- `pub use token_credentials::certificate_credentials::ClientCertificateCredentialExt` exposes local certificate credentials.
- `STORAGE_VENDOR_NAME_AZURE` is the canonical vendor string `"azure"`.

## Control Flow
There is no runtime control flow beyond module initialization. Consumers import the re-exported types and construct them from kvproto/shared cloud config.

## State And Persistence Behavior
No state is held in this file; state lives in the provider structs re-exported here.

## Dependencies And Integration Points
This file integrates the Azure crate into shared provider selection through stable vendor naming and public exports.

## Risks And Edge Cases
The crate re-exports `Config` from `azblob`; KMS config is a separate shared type, so imports can be ambiguous. Vendor string changes would break configuration matching.

## Test Signals
No direct tests. Coverage is indirect through `azblob.rs`, `kms.rs`, and downstream provider selection.
