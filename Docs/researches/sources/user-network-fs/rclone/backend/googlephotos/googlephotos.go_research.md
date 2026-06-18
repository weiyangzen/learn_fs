# sources/user-network-fs/rclone/backend/googlephotos/googlephotos.go

## Purpose
This file implements rclone's Google Photos backend. It exposes Google Photos as a virtual filesystem with media views, album views, shared album views, an upload staging tree, and a feature/favorites view, while respecting Google Photos API limitations around app-created data, mtimes, deletion, and original downloads.

## Important APIs, Types, And Control Flow
Key types are `Options`, `Fs`, `Object`, and `uploadedItem`. `init` registers `gphotos`, configuration warnings, read-only/read-size/start-year/include-archived/proxy options, and batcher options. `NewFs` creates an OAuth client, normalizes root, initializes authenticated and unauthenticated REST clients, pacer, album caches, upload dirtree, and a `batcher.Batcher`; it detects file-root paths through `patterns.match`.

Authentication support includes `UserInfo`, `Disconnect`, and `fetchEndpoint`, which read OpenID configuration endpoints and use the OAuth token source for revocation. `errorHandler` accepts JSON API errors and image/404 responses.

Listing uses `listAlbums`, `list`, `itemToDirEntry`, `listDir`, `listUploads`, and `List`. Albums are cached by shared/non-shared key. Media listing calls `/mediaItems:search`, adds `IncludeArchivedMedia` unless listing an album, skips duplicate first items across pages, replaces slashes in filenames, and deduplicates duplicate filenames by adding `{ID}`. `List` itself delegates path interpretation to `pattern.go`.

Writes use `Mkdir`, `Put`, `Object.Update`, `commitBatch`, and `commitBatchAlbumID`. `Mkdir` can create app albums or synthetic upload directories. `Update` validates that the virtual path is uploadable, creates or finds albums where required, rejects read-only or non-writeable albums, uploads bytes to `/uploads` to receive a token, then commits tokens through `/mediaItems:batchCreate`, batching by album ID. Uploads under `upload/` are also stored in the local `uploaded` dirtree.

Object operations include ID-aware `readMetaData`, optional size probing with `HEAD`, `downloadURL`, `Open` with optional gphotosdl proxy, unsupported hashes and modtime updates, and `Remove`, which only removes media from writable app-created albums through `batchRemoveMediaItems`. Album deletion is explicitly unsupported.

## State And Persistence
Runtime state includes OAuth token source, REST clients, pacer, start time for virtual directories, album caches, uploaded local dirtree, create mutex, and batcher. Remote persistence includes created albums and uploaded media items. Local `uploaded` state is process memory only, so the upload virtual tree is not durable across backend instances. Google OAuth token persistence is handled by rclone's OAuth utilities.

## Dependencies And Integration Points
The backend integrates `oauthutil`, `rest`, `batcher`, `dirtree`, `encoder`, Google OAuth endpoints, and the pattern and album helpers in this package. It implements `fs.UserInfoer`, `fs.Disconnecter`, `fs.MimeTyper`, and `fs.IDer`; it intentionally does not expose hashes or settable mtimes.

## Risks And Test Signals
Risks are dominated by Google Photos API restrictions and policy changes: only app-created data can be downloaded/edited under current scopes, albums cannot be deleted through this code, uploaded-tree state is memory-only, album cache invalidation is missing, filenames can collide, and `Remove` assumes `f.albums[false]` has been populated. Batch result ordering and album grouping are critical. Tests should cover virtual path matching, read-only mode, non-writeable albums, duplicate filenames, ID-based lookup, batch failures, proxy download URLs, `ReadSize`, and upload directory persistence limits.
