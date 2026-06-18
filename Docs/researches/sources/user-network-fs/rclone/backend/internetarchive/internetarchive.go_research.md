# sources/user-network-fs/rclone/backend/internetarchive/internetarchive.go

## Purpose
Implements an Internet Archive backend using IA's native IAS3/frontend APIs instead of a generic S3-compatible backend. It exposes IA items as buckets and item files as rclone objects, with metadata, hashes, public links, server-side copy, cleanup, usage reporting, and optional archive-processing wait behavior.

## Important APIs, Types, and Functions
`Options` contains IAS3/front endpoints, optional auth keys, item metadata, derive flag, checksum behavior, wait timeout, and encoder. `Fs` stores root, options, IAS3 and frontend REST clients, pacer, and context. `Object` stores remote, modtime, size, server hashes, and raw metadata JSON. API models include `IAFile`, `MetadataResponse`, `MetadataResponseRaw`, and `ModMetadataResponse`.

Core methods include `NewFs`, `split`, `requestMetadata`, `listAllUnconstrained`, `List`, `ListR`, `NewObject`, `Put`, `Object.Update`, `Object.Open`, `Object.Remove`, `SetModTime`, `Metadata`, `Copy`, `PublicLink`, `CleanUp`, `About`, `waitFileUpload`, `waitDelete`, `appendItemMetadataHeaders`, `listOrString`, and path/time helpers.

## Control Flow
`NewFs` parses endpoints, trims root, configures `rest.Client`s for IAS3 and frontend, applies LOW authorization when keys exist, configures S3-style pacing, and probes whether the root is a file. Listing starts from frontend `/metadata/:item`, converts metadata files into objects and virtual directories, then filters direct children for `List` or recursive descendants for `ListR`.

Uploads construct IAS3 `PUT` headers for rclone mtime/update tracking, auto bucket creation, cascade delete, old-version behavior, optional checksum, item metadata, and derive behavior. After the PUT, `waitFileUpload` either returns quickly with best-effort metadata or polls frontend metadata until a tracker and size match. Deletes call IAS3 `DELETE` and optionally poll until metadata disappears. Server-side copy uses IAS3 copy-source headers and the same tracker/wait flow.

`SetModTime` patches file metadata through the frontend metadata write API by removing and re-adding `rclone-mtime`. `Metadata` unmarshals raw IA file metadata, keeps only first values for multi-valued keys, preserves IA's original `mtime` as `rclone-ia-mtime`, and overwrites `mtime` with rclone's parsed modtime.

## State and Persistence
Remote state is IA item file metadata and IAS3 object data. Local persistent state is limited to config. Rclone mtimes are stored as IA file metadata under `rclone-mtime`, while update completion is tracked with a random `rclone-update-track` value. Directories are virtual and inferred from file paths. `history/` is treated as trash for cleanup and usage.

## Dependencies and Integration Points
Uses rclone `fs`, `configstruct`, `fserrors`, `fshttp`, `hash`, `bucket`, `encoder`, `pacer`, `random`, and `rest`, plus `ncw/swift` time parsing for IA float mtimes. It integrates with both IA IAS3 and archive.org frontend metadata/download endpoints.

## Risks and Edge Cases
`Mkdir` and `Rmdir` are no-ops because IA directories are virtual, which may surprise callers. Metadata polling can time out silently by design when `wait_archive` expires. When `wait_archive` is disabled, returned object size/hash may be intentionally unknown or blank after writes. `listAllUnconstrained` builds directory entries from all item metadata, so large IA items may make every list expensive. Path trimming is delicate because bucket/root paths are mixed with encoded and standard paths. `Copy` and upload rely on update trackers in metadata, which can be delayed by IA processing queues.

## Test Signals
The local test file is only an integration harness against `TestIA:lesmi-rclone-test/`. There are no unit tests for metadata parsing, path trimming, wait polling, item metadata header generation, or no-op directory semantics in this subset.
