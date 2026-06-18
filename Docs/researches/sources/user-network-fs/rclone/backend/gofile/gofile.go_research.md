# sources/user-network-fs/rclone/backend/gofile/gofile.go

## Purpose
This file implements rclone's Gofile backend. It registers the `gofile` remote, authenticates with bearer token, discovers and caches account/root folder IDs, maps Gofile folders to rclone directories through a directory cache, and implements listing, upload, update, removal, quota, public links, server-side moves/copies, directory modtimes, and duplicate-support behavior.

## Important APIs, Types, And Control Flow
Key types are `Options`, `Fs`, `Object`, and `Directory`. `NewFs` configures the REST client, sets the Authorization header, reads `account_id` and `root_folder_id` when missing and writes them back through the config mapper, initializes `dircache.DirCache`, and handles the "root is a file" case with a temporary parent `Fs`.

`listAll` is the primitive for paginated `/contents/{id}` listing; it supports directory-only, file-only, and server-side name filtering, decodes remote names through the encoder, and maps `error-notFound` to `fs.ErrorDirNotFound`. `List` lists one directory via `dirCache.FindDir`; `ListR` asks Gofile for recursive listings up to `maxDepth` and recurses manually when the API truncates nested children. `itemToDirEntry` caches folder IDs and constructs either `Directory` or `Object`.

Writes flow through `Put`, `PutUnchecked`, and `Object.Update`. `Put` checks for an existing object and updates it; `PutUnchecked` allows duplicates. `Update` finds or creates the parent folder, clears the old object ID while uploading a replacement, uploads multipart data to `api.DirectUploadURL`, and deletes the old item only after upload success. Directory operations use `CreateDir`, `Mkdir`, `Rmdir`, `Purge`, and `DirSetModTime`.

Server-side transforms use `rename`, `setModTime`, `move`, `moveTo`, `copy`, and `copyTo`. `Move` and `DirMove` adjust paths through dircache and Gofile move calls. `Copy` creates a new duplicate, then removes an existing destination only after the copy succeeds and resets modtime because Gofile copy does not preserve it. `PublicLink` creates or removes direct links for files or directories.

## State And Persistence
Local runtime state includes REST client, pacer, features, and directory cache. Config persistence is explicit: discovered `account_id` and `root_folder_id` are written into the config mapper. Remote persistent state includes Gofile folders/files, item modtimes, direct links, copied/moved items, and deletes. Directory cache entries are invalidated on purge and directory moves.

## Dependencies And Integration Points
The backend uses rclone `rest`, `dircache`, `list.Helper`, `pacer`, `fshttp`, `encoder`, and hash support. It implements many optional interfaces: `Purger`, `PutStreamer`, `PutUncheckeder`, `Copier`, `Abouter`, `Mover`, `DirMover`, `DirCacheFlusher`, `PublicLinker`, `MergeDirser`, `DirSetModTimer`, `ListRer`, `IDer`, `MimeTyper`, `ParentIDer`, and directory `SetModTimer`. It exposes MD5 from Gofile metadata.

## Risks And Test Signals
Risks include API status-string changes, duplicate-file semantics, replacing an existing file by upload-then-delete, stale dircache after direct remote changes, pagination and recursive max-depth behavior, rate-limit sleeps blocking goroutines, direct link cleanup failures, and copy/move response maps missing the source ID. Tests should cover paged listings, duplicate names, update failure preserving the old object, public link create/delete, move/copy into new and existing destinations, quota mapping, and `max_age` of dircache under external changes.
