# sources/sync-backup/kopia/repo/blob/azure/azure_storage.go

Purpose: implements the Azure Blob Storage provider for Kopia's `blob.Storage` interface.

Important APIs/types/functions: `azStorage`, `GetBlob`, `getBlobWithVersion`, `GetMetadata`, `translateError`, `PutBlob`, `DeleteBlob`, `ExtendBlobRetention`, `ListBlobs`, `putBlob`, `retryDeleteBlob`, `New`, `getAZService`, and provider `init`.

Control flow: reads validate range, create a versioned blob client, issue `DownloadStream`, optionally perform a one-byte request for zero-length reads, copy data, and verify length. Metadata reads map Azure properties and Kopia timestamp metadata. Writes reject unsupported `DoNotRecreate`, normalize retention mode to Azure locked semantics, upload a block blob with metadata and optional immutability policy, and return server mod time. Deletes ignore not-found and, when immutability blocks deletion, create/delete an unlocked temporary version as a soft-delete marker workaround. `New` validates container, builds a client using SAS, shared key, client secret, certificate, or workload identity, optionally wraps PIT and retrying storage, and verifies listing.

State and persistence behavior: blob contents, metadata timestamps, versions, immutability policies, and delete markers live in Azure. The provider itself keeps client/container/options only.

Dependencies/integration points: uses Azure SDK clients, Kopia timestamp metadata, retrying wrapper, point-in-time/readonly wrapper, and storage registry. Risks include no `DoNotRecreate` support, provider-specific metadata key casing, immutable delete complexity, credential-mode ambiguity, and cloud propagation failures. Tests cover user agent, live storage operations, invalid credentials/container/blob, credential modes, immutability, and versioned PIT behavior.
