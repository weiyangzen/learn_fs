# sources/sync-backup/kopia/repo/blob/azure/azure_options.go

Purpose: defines JSON options for Azure Blob Storage-backed repositories.

Important APIs/types/functions: `Options` includes container, storage account/key, SAS token, prefix, TLS/storage-domain knobs, throttling limits, point-in-time view timestamp, and Azure AD credential variants: tenant/client secret, client certificate, and federated token file.

Control flow: this file has no functions; validation and client construction are in `azure_storage.go`. JSON tags and `kopia:"sensitive"` annotations drive persistent config shape and secret handling.

State and persistence behavior: the struct is serialized into `blob.ConnectionInfo` for local repository config. Fields such as `StorageKey`, `SASToken`, `ClientSecret`, `ClientCertificate`, and federated token path influence authentication without being persisted elsewhere by this file.

Dependencies/integration points: consumed by Azure storage creation, throttling wrappers, point-in-time wrappers, and CLI/config code. Risks include backward-compatibility pressure on field names, multiple mutually exclusive credential modes with validation deferred to `getAZService`, and `DoNotUseTLS` enabling insecure HTTP credentials only when client options permit it. Integration tests cover several credential variants.
