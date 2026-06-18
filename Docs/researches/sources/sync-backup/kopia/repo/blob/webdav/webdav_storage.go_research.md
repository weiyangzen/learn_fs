# sources/sync-backup/kopia/repo/blob/webdav/webdav_storage.go

Purpose: implements WebDAV-backed Kopia blob storage using the shared sharded layout, HTTP/WebDAV file operations, optional temp-file renames, retry-on-transient errors, and certificate-fingerprint trust.

Important APIs/types/functions: `davStorage` embeds `sharded.Storage`; `davStorageImpl` implements sharded `Impl`. Key methods are `GetBlobFromPath`, `GetMetadataFromPath`, `PutBlobInPath`, `DeleteBlobInPath`, `ReadDir`, `ConnectionInfo`, `DisplayName`, `translateError`, `httpErrorCode`, `isRetriable`, and `New`.

Control flow: `New` creates a `gowebdav.Client`, disables transport compression via `Accept-Encoding: identity`, optionally sets a TLS transport trusting one certificate, constructs sharded storage, and returns a retrying wrapper. Reads use full or ranged streams, special-case zero-length reads, translate HTTP errors, and exact-length-check output. Writes buffer the whole blob, write either final path or random temp path, create missing parent directories on first failure, optionally rename temp to final path, and fill `GetModTime` via metadata.

State and persistence behavior: blobs are `.f` files in the sharded layout under the WebDAV root. Non-atomic mode leaves temporary random names only if write/rename cleanup fails. `SetModTime`, retention, and do-not-recreate are unsupported.

Dependencies/integration: depends on `gowebdav`, Kopia retry helpers, TLS utility, sharded storage, and blob sentinel errors. It shares on-disk layout with filesystem storage.

Risks and edge cases: `math/rand` temp names are not cryptographic. Some servers return 403 instead of 404 for missing parents, so mkdir retry logic matters. HTTP errors are parsed from `os.PathError` text. Atomic direct writes can expose partial data if the server does not provide atomic PUT semantics.

Test signals: `webdav_storage_test.go` runs external/built-in WebDAV validation, many shard specs, auth handling, and a 404-to-403 transform for missing PUTs.
