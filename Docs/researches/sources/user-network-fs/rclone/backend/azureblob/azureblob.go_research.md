# Research: sources/user-network-fs/rclone/backend/azureblob/azureblob.go

## Purpose
This file implements rclone's Microsoft Azure Blob Storage backend on supported platforms. It registers the `azureblob` remote, maps rclone filesystem operations to Azure Blob SDK APIs, handles containers as buckets, supports metadata/tags, tiering, directory markers, gzip behavior, chunked upload, server-side copy, and cleanup of problematic uncommitted block state.

## Important APIs, Types, and Functions
- `Options` embeds shared Azure auth options and adds blob-specific knobs such as `chunk_size`, copy concurrency/cutoff, access tier, archive overwrite policy, checksum disable, encoding, public access, directory markers, no-head behavior, snapshot delete policy, and gzip decompression.
- `Fs` stores backend state: root, parsed options, Azure `service.Client`, cached `container.Client`s, auth mode flags, bucket cache, pacer, upload/copy concurrency tokens, public access, gzip warning state, and cached user delegation credentials.
- `Object` stores per-blob state: remote, modtime, base64 MD5, size, MIME type, tier, user metadata, blob tags, and content encoding.
- Registration in `init` exposes metadata help, config options, and feature flags.
- `NewFs` parses config, validates access tier/public access/list chunk/chunk size, constructs auth client via `auth.NewClient`, configures gzip accept-encoding policy, initializes caches and features, and detects when the root path names an existing blob.
- Listing is implemented by `list`, `listDir`, `listContainers`, `ListP`, and `ListR` using Azure pagers.
- Upload paths are `Put`, `PutStream`, `prepareUpload`, `uploadSinglepart`, `OpenChunkWriter`, `azChunkWriter.WriteChunk`, `azChunkWriter.Close`, and `uploadMultipart`.
- Copy paths are `Copy`, `copySinglepart`, `copyMultipart`, `getAuth`, and `getUserDelegation`.
- Metadata helpers include `mapMetadataToAzure`, `assembleCopyParams`, `applyMappedMetadata`, `setMetadata`, `Metadata`, `SetModTime`, and decode helpers for property/download/list responses.
- Container and directory operations are `Mkdir`, `makeContainer`, `createDirectoryMarker`, `Rmdir`, `Purge`, `deleteContainer`, and `isEmpty`.
- Tier operations are `AccessTier`, `SetTier`, `GetTier`, and `parseTier`.

## Control Flow
Reads and listings split rclone remotes into container and blob path using `bucket.Split` plus encoding transforms. At the root, list operations enumerate containers; below a container, blob hierarchy/list pagers produce `fs.Dir` and `Object` entries. Directory marker support treats zero-size slash-suffixed blobs or `hdi_isfolder=true` metadata as directories and can create/remove marker blobs during mkdir/rmdir.

Uploads first call `prepareUpload`, which ensures parent containers/directories, maps metadata and tags, sets default content type, preserves mtime in user metadata, optionally computes Content-MD5 from source hash, and applies upload headers. Small known-size uploads read into a retryable multipart buffer and call `blockblob.Upload`; large or unknown-size uploads use rclone's multipart helper and `OpenChunkWriter`. Each chunk gets a random-suffixed block ID, transactional MD5, retry pacing, and later `CommitBlockList` with metadata, tags, tier, and HTTP headers.

Copies first validate same backend type, create parents, then choose single-part `StartCopyFromURL` or multipart `StageBlockFromURL` plus `CommitBlockList`. Same-storage-account copies prefer Copy Blob when enabled. Microsoft Entra ID cross-account copies force multipart because token auth is not used directly by Copy Blob. Source auth is converted to a plain URL for same-account copies, a user-delegation SAS for token credentials, a shared-key SAS for shared key credentials, or the existing URL for anonymous/SAS remotes.

Downloads reject archive-tier blobs, honor range/seek options, issue `DownloadStream`, refresh metadata from the download response, and either return compressed bytes or wrap a gzip reader when `--azureblob-decompress` is enabled.

## State and Persistence
Persistent remote state includes containers, block blobs, metadata, tags, content headers, access tiers, snapshots deletion behavior, and optional directory marker blobs. Local backend state caches container clients, container existence/deletion status, object metadata, user delegation SAS keys, and warning `sync.Once`s. `metadataMu` is a package-level lock protecting object metadata map access. Uncommitted blocks are remote transient state; `clearUncommittedBlocks` attempts to resolve `InvalidBlobOrBlock` by re-committing existing committed block IDs or committing an empty list and deleting the created blob.

## Dependencies and Integration Points
The backend integrates with Azure `azblob` service/container/blob/blockblob clients, Azure SAS/user delegation APIs, rclone `fs` optional interfaces, config mapping, bucket cache, encoders, pacer retries, chunk size calculator, multipart upload helper, memory pool accounting, transfer accounting, and `errgroup`. It shares auth with Azure Files through `backend/azureblob/auth`.

## Risks and Edge Cases
- Directory marker logic must distinguish real zero-byte files from folders; metadata or trailing slash can make a blob appear as a directory.
- Metadata is case-insensitive in Azure but normalized to lower case locally; duplicate casing could otherwise break shared-key signing.
- `getMetadata` creates pointers to range-loop values, which is acceptable because each `v` escapes per iteration but remains subtle.
- `NoHeadObject` can create objects without metadata until a later read/download fills fields.
- Gzip decompression makes size and hash unknown and changes download bytes, so sync comparisons can be affected.
- Archive-tier overwrite can delete the old blob first when `archive_tier_delete` is enabled, which is an explicit data-loss tradeoff if the replacement upload fails.
- Single-part copy sets mapped headers post-copy; there is a window where copied headers may not yet match requested metadata.
- Multipart copy uses large concurrency and optional global token limiting; misconfigured high concurrency can stress service limits.
- User delegation SAS caching depends on wall-clock expiry and token permissions.
- The retry path for `InvalidBlobOrBlock` serializes around in-flight operations and clears uncommitted blocks only once; overlap with other writers to the same blob remains hazardous.

## Test Signals
`azureblob_internal_test.go` covers block ID creation/validation, backend feature flags, recovery from uncommitted blocks during multipart upload/copy, metadata/header/tag propagation across upload and copy paths, invalid tag rejection, mtime injection under metadata mode, and gzip download behavior. `azureblob_test.go` runs full fstests twice, once with directory markers enabled, tests chunked upload configuration hooks, and validates accepted access tiers.
