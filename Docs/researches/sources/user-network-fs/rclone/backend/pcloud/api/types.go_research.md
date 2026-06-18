# sources/user-network-fs/rclone/backend/pcloud/api/types.go

Purpose: defines JSON-facing schemas and helper methods for the pCloud backend.

Important APIs/types/functions: `Time` marshals/unmarshals pCloud's RFC1123Z timestamps. `Error` models pCloud's `result`/`error` response pattern and `Update` converts transport or nonzero API results into Go errors. `Item` models files/folders and `ModTime` falls back from modified time to created time. Response types cover item operations, file descriptors, file checksums and writes, uploads, download links, public links, user quota, and diff entries.

Control flow: most structs are passive decode targets. Active logic is in `Time`, `Error.Update`, `Item.ModTime`, and `GetFileLinkResult.IsValid`/`URL`. `IsValid` requires at least one host and an expiry more than 30 seconds in the future.

State and persistence: no local persistence. Types represent remote pCloud state: IDs, paths, folder trees, hashes, file descriptors, quotas, public links, and diff streams.

Dependencies/integration: depends only on `fmt` and `time`. Consumed by `pcloud.go` and `writer_at.go` through `rest.Client.CallJSON`.

Risks/test signals: strict timestamp parsing may break on API format drift. `GetFileLinkResult.URL` always chooses the first host. `DiffResult.Entries` uses untyped maps, so change-notify parsing can silently skip unexpected shapes. There are no direct tests; integration tests exercise decoding indirectly.
