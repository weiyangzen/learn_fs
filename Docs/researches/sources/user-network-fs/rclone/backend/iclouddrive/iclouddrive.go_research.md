# sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive.go

## Purpose
Implements the writable iCloud Drive rclone backend for non-Plan9/non-Solaris builds. It adapts Apple iCloud Drive API calls to rclone `fs.Fs`, `fs.Object`, `fs.Mover`, `fs.DirMover`, `fs.Purger`, `fs.Copier`, `fs.Disconnecter`, and `fs.DirCacheFlusher` interfaces.

## Important APIs, Types, and Functions
`Options` carries Apple ID/password/client/cookie/trust-token fields plus the multi-encoder. `Fs` stores backend identity, root, root ID, config mapper for persisted auth, `dircache.DirCache`, iCloud API client, drive service, and pacer. `Object` stores remote, size, modtime, created time, drive/document/item IDs, ETag, and download URL.

Core directory helpers are `findItem`, `findLeafItem`, `FindLeaf`, `FindPath`, `FindDir`, `IDJoin`, `putFolderCache`, and `CreateDir`. Listing and object creation run through `listAll`, `List`, `NewObject`, `NewObjectFromDriveItem`, `readMetaData`, and `setMetaData`. Mutating behavior is in `Put`, `Object.Update`, `Object.Remove`, `Move`, `DirMove`, `purgeCheck`, `Purge`, and `Rmdir`. `Copy` is present but deliberately returns `fs.ErrorCantCopy` because the iCloud copy endpoint is marked broken.

## Control Flow
`NewFs` builds an authenticated iCloud client for `api.WsDrive`, trims the configured root, initializes a pacer, obtains `DriveService`, and creates a `dircache` rooted at `FOLDER::com.apple.CloudDocs::root`. If root lookup fails, it probes the parent as a possible file root and returns `fs.ErrorIsFile` when appropriate.

Directory lookup flows through `dircache`; `FindLeaf` lists all children under a normalized ID, compares names case-insensitively after NFC normalization, rejects file leaves as `fs.ErrorIsFile`, and returns an ID joined with the ETag. `List` resolves a dir ID, fetches all children through `GetItemByDriveID`, decodes names/extensions, caches folders, and converts files into `Object`s.

Uploads remove an existing file first, create an upload document, upload bytes, then call `UpdateFile` with receipt/signature/key/size and mtime/btime. Downloads fetch a fresh download URL by drive ID before streaming with range options. Moves split into an optional parent move followed by optional rename, because iCloud exposes them as separate calls.

## State and Persistence
Auth state and disconnect cleanup are delegated to shared iCloud helpers through the config mapper and `disconnectClient`. Directory state is cached in `dircache` as `drivewsid#etag`; cache entries are flushed after destructive operations. Object state is populated from API metadata and refreshed after upload/update. Empty files are emulated on download by returning an empty reader because Drive does not support real empty-file storage.

## Dependencies and Integration Points
The file depends on `backend/iclouddrive/api` for Drive endpoints, rclone `fs` interfaces, `configmap`, `fserrors`, `hash`, `dircache`, `encoder`, `pacer`, and Unicode normalization. It uses rclone's pacer retry contract around every remote call and uses the backend encoder before sending names to iCloud or exposing them to rclone.

## Risks and Edge Cases
iCloud occasionally returns status `unknown`; the backend alternates between ignoring unknown results for idempotent-looking operations and retrying unknown results for operations where final state is uncertain. `findItem` assumes `resp.StatusCode` is available when `item == nil`, which depends on API behavior after errors. `Object.Update` trashes the old file before completing the new upload, so a later create/upload/update failure can lose the previous version. ETag handling is embedded in string IDs using `#`, so any unexpected delimiter in IDs would be dangerous, though `IDJoin` strips prior ETags. Server-side copy is dead code after an unconditional `ErrorCantCopy`.

## Test Signals
Drive-specific local tests are not in this file's package; integration coverage is provided by `iclouddrive_test.go` against `TestICloudDrive:`. Important untested local seams include `ignoreResultUnknown`, `retryResultUnknown`, empty-file emulation, ID/ETag joining, and rollback behavior during update failures.
