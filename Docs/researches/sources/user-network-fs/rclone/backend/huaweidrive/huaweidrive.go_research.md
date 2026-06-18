
# sources/user-network-fs/rclone/backend/huaweidrive/huaweidrive.go

## Purpose
This file implements the Huawei Drive rclone backend. It handles OAuth, root detection, regional endpoint switching, directory caching, listing, upload modes, server-side copy/move, metadata, recycle cleanup, change notification, user info, and disconnect.

## Important APIs, Types, And Control Flow
`init` registers backend options and metadata capabilities. `NewFs` builds an OAuth REST client, resolves the concrete drive root ID via `/files/root` unless configured, optionally switches to a regional domain using `/about`, creates a `dircache.DirCache`, and handles root-as-file detection. `FindLeaf` and `CreateDir` satisfy dircache lookup/create hooks. `listDirectoryWithFilter` builds Huawei query strings and paginates `/files`. `List` and `ListR` populate dirs/objects and cache item metadata for later change notification. `Put` updates existing objects or recovers duplicate create races by looking up and updating. `Object.Update` spools unknown-size streams to a temp file, creates parents, and chooses empty, multipart, or resumable upload. Copy/move use `/copy` or PATCH updates and include verification/fallback for cross-directory move quirks. `Metadata` and `SetMetadata` map system/user metadata to Huawei fields/properties. `ChangeNotify` polls start cursors and change lists, deduplicates path notifications, and uses dircache plus item cache to resolve old and new paths.

## State And Persistence
Persistent remote effects include file/folder creation, upload replacement, deletion/recycle, directory purge, metadata updates, copies, moves, and recycle-bin cleanup. Local process state includes directory ID cache, item metadata cache, root folder ID, regional URLs, OAuth token in rclone config, and temporary files for unknown-size uploads. Huawei does not preserve requested modification times, so `Precision` returns `fs.ModTimeNotSupported`.

## Dependencies And Integration Points
The backend depends on Huawei DTOs, rclone `dircache`, OAuth, rest, pacer, metadata helpers, MIME detection, encoder, and standard multipart/HTTP packages. It implements many optional rclone interfaces: `Purger`, `Copier`, `Mover`, `DirMover`, `ListRer`, `CleanUpper`, `Abouter`, `ChangeNotifier`, `UserInfoer`, `Disconnecter`, `DirCacheFlusher`, `MimeTyper`, and `Metadataer`.

## Risks And Test Signals
Upload code buffers multipart uploads fully in memory below cutoff and spools unknown-size uploads to a local temp file. Resumable upload chunk size is clamped at runtime rather than rejected at config parse. Empty-file upload removes an existing object first, so replacement failure can lose the old file. `Remove` assumes `o.id` is populated. Query filters are manually formatted strings; escaping only handles single quotes in filenames. Error mapping collapses HTTP 409 to `fs.ErrorDirExists`, which may be too broad. Change notification only resolves parents already in dircache. Tests should cover root ID detection, regional switching, list pagination, dircache invalidation, duplicate create race recovery, all upload modes, metadata read/write, empty SHA256 behavior, cross-directory move fallback, cleanup, retry mapping, and cursor polling.
