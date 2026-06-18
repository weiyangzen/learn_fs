# sources/storage-engines/tikv/components/cloud/azure/src/azblob.rs

## Purpose
Implements TiKV's Azure Blob storage backend behind the shared `cloud::blob` traits. It translates `kvproto::brpb::AzureBlobStorage` into a local `Config`, chooses an Azure authentication path, builds `ContainerClient`s, and exposes `put`, `get`, and `get_part` for backup/restore flows. Iteration and deletion are intentionally unsupported here.

## Important APIs, Types, And Functions
- `Config` stores bucket/prefix/endpoint, explicit account/shared-key/SAS credentials, environment credentials, Azure AD client-secret credential info, encryption scope, and customer-provided encryption key data. Its custom `Debug` redacts secrets.
- `Config::from_input` validates the required bucket field, converts empty strings to `None`, loads environment variables, and maps `AzureCustomerKey` into `EncryptionCustomer`.
- `Config::get_account_name`, `parse_plaintext_account_url`, and `parse_env_plaintext_account_url` implement account/key lookup and connection-string construction.
- `AzureUploader` reads the whole `PutResource` into memory, applies upload headers for encryption scope, customer key, or access tier, and retries one `put_block_blob` inside a 15 minute timeout.
- `ContainerBuilder` abstracts Azure SDK client construction. Implementations are `DefaultContainerBuilder`, `SharedKeyContainerBuilder`, and `TokenCredContainerBuilder`.
- `TokenCredContainerBuilder` caches bearer tokens with a `RwLock<Option<(AccessToken, Arc<ContainerClient>)>>` and an async mutex for refresh coordination.
- `AzureStorage` implements `BlobStorage`; `IterableStorage` and `DeletableStorage` return the shared unsupported error.

## Control Flow
`AzureStorage::from_input` calls `Config::from_input`, then `AzureStorage::new`. `new` validates encryption/access-tier combinations and picks credentials in priority order: explicit SAS token, explicit shared key, Azure AD env client-secret variables, environment shared key, then Azure SDK `DefaultAzureCredential`. Reads call `maybe_prefix_key`, build a blob `get` request with optional byte range and optional customer encryption key, collect Azure response chunks into a `Vec<u8>`, and expose that vector as an async reader. Writes call `AzureUploader::run`, which buffers all input with `cloud::blob::read_to_end`, retries `upload`, and records `AZBLOB_UPLOAD_DURATION`.

## State And Persistence Behavior
The module persists and retrieves object bytes in Azure Blob Storage. Local mutable state is credential/client cache only: shared-key/SAS builders hold a stable `ContainerClient`; token builders cache access tokens until they approach expiry. Prefix handling is string-based and prepends `prefix.trim_end_matches('/')` to object names.

## Dependencies And Integration Points
It depends on `azure_storage`, `azure_storage_blobs`, `azure_identity`, `azure_core`, `oauth2`, `tokio`, `futures`, TiKV `tikv_util::stream::retry`, and shared `cloud::blob`/`cloud::metrics` contracts. Its input and customer key types come from `kvproto::brpb`. It is re-exported by the Azure crate root.

## Risks And Edge Cases
Uploads and reads buffer complete objects into memory, which is risky for large backup files. Azure SDK errors are generally mapped to `InvalidInput` except timeouts, reducing retry fidelity. Token refresh uses `std::sync::RwLock` inside async code, though lock holds are short. List and delete are unsupported. Header selection for upload is mutually exclusive: encryption scope, customer key, then access tier.

## Test Signals
Unit tests cover backend URL formatting, env credential loading and debug redaction, config validation for access-tier/encryption conflicts, and an ignored Azurite put/get test. Active tests do not cover token refresh, range reads, or Azure network error mapping.
