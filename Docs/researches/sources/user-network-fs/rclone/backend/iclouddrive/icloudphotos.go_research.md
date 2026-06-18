# sources/user-network-fs/rclone/backend/iclouddrive/icloudphotos.go

## Purpose
Implements the read-only iCloud Photos backend, sharing auth/config with the iCloud Drive package while exposing libraries, albums, nested folders, photos, metadata, recursive listing, and change notification through rclone interfaces.

## Important APIs, Types, and Functions
`PhotosFs` stores root, options, iCloud client, config mapper, pacer, `dircache`, HTTP client, lazy `PhotosService`, and a mutex. `PhotosObject` stores remote metadata plus CloudKit master/zone/resource identifiers required to obtain fresh download URLs.

Key APIs are `NewFsPhotos`, `photosService`, `List`, `NewObject`, `newPhotosObject`, `FindLeaf`, `resolveAlbum`, `resolveAlbumPath`, `parseAlbumDirID`, `ListR`, `ChangeNotify`, `notifyZoneChange`, `Metadata`, and `Open`. Write operations `Put`, `Mkdir`, `Rmdir`, `CreateDir`, `PhotosObject.Update`, and `PhotosObject.Remove` return `fs.ErrorNotImplemented`.

## Control Flow
`NewFsPhotos` authenticates against `api.WsPhotos`, builds a read-oriented feature set, and initializes `dircache` at synthetic `photos-root`. Like Drive, it probes whether the configured root is actually a file and can return `fs.ErrorIsFile`.

`List` dispatches by directory ID shape: `photos-root` lists libraries, `lib:<library>` lists albums for a library, and `album:<library>:<path>` lists child albums for folder albums or files for leaf albums. `FindLeaf` mirrors this state machine for `dircache`, resolving libraries, top-level albums, and nested child albums. `NewObject` resolves parent album and then performs a name lookup inside the album.

`ListR` resolves the starting directory, emits directories via `list.Helper`, collects leaf album jobs, and lists album photos with a goroutine pool sized by `fs.GetConfig(ctx).Checkers`. `Open` performs a fresh `LookupDownloadURL` and streams through the configured HTTP client with rclone range headers. `ChangeNotify` starts a goroutine that receives poll intervals, polls CloudKit change tokens, and notifies affected directories.

## State and Persistence
The backend has no write persistence because it is read-only. It caches directory IDs in `dircache` and caches the lazily constructed `PhotosService`; `DirCacheFlush` resets both dircache and API-layer caches. `startTime` is used as a stable synthetic modtime for library/album directories. Object metadata is derived from API photo fields and returned through rclone metadata keys.

## Dependencies and Integration Points
Depends on `backend/iclouddrive/api` Photos types, rclone `fs`, `fshttp`, `hash`, `list`, `dircache`, and `pacer`. It uses the same retry helpers as Drive and the same encoder options. CloudKit record IDs, zones, and resource keys are integration-critical because download URLs are not treated as durable.

## Risks and Edge Cases
`parseAlbumDirID` strips the prefix with `strings.TrimPrefix`; callers usually guard with `HasPrefix`, but the helper itself accepts some non-`album:` strings as valid if they contain a colon. `ListR` protects `list.Helper` with a mutex but still depends on album caches and context cancellation working correctly under parallel listing. Change notification invalidates directories coarsely, especially when rooted at missing nested albums. Read-only methods returning `ErrorNotImplemented` must remain consistent with advertised features.

## Test Signals
`icloudphotos_test.go` covers smart album definitions, metadata formatting, nested album resolution, `FindLeaf`, `ListR` recursion from root and folder roots, and zone-change notification scope. There is no live integration harness in this file; real CloudKit behavior is exercised only when broader backend integration tests are configured.
