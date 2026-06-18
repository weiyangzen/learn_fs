# sources/sync-backup/kopia/repo/blob/sharded/sharded.go

Purpose: provides reusable directory-sharding logic for providers whose blobs are files in a hierarchical namespace, such as filesystem, SFTP, and WebDAV.

Important APIs/types/functions: `Impl` is the provider-specific file API; `Storage` wraps an `Impl`, root path, sharding options, and cached `Parameters`; `CompleteBlobSuffix` marks complete blobs as `.f`. Methods implement the blob contract: `GetBlob`, `ListBlobs`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `GetShardedPathAndFilePath`, plus parameter loading through `getParameters`.

Control flow: operations first load or create `.shards`, compute shard directory and final file path, then delegate to the provider-specific `Impl`. Listing walks directories through a `parallelwork.Queue`, filters `.f` files, reconstructs full blob IDs from path prefix plus file name, applies caller prefix filtering, and streams metadata through a result channel while callback errors stop processing.

State and persistence behavior: sharding parameters are cached in memory and, if absent, initialized from defaults and best-effort written to `.shards`. Blob files are identified by `.f`; unrelated files and incomplete names are ignored during listing.

Dependencies/integration: used by providers that implement `Impl`; depends on `Parameters` from `sharded_parameters.go`, gather buffers for `.shards`, `parallelwork`, `errgroup`, and blob metadata/error types.

Risks and edge cases: if `.shards` exists but is malformed, operations fail until a valid parameters file is loaded or the file is removed. Listing concurrency must close channels correctly on callback failure. The default shard layout differs between create and open for legacy compatibility.

Test signals: `sharded_test.go` verifies legacy/latest default layouts, multiple shard specs, ignored foreign files, prefix listing under overrides, malformed `.shards`, and deep clone behavior.
