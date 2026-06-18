# sources/user-network-fs/rclone/backend/sharefile/sharefile.go

## Purpose

`sharefile.go` implements the main rclone backend for Citrix ShareFile. It registers the `sharefile` remote, performs OAuth setup and endpoint discovery, maps rclone `fs.Fs`/`fs.Object` operations onto ShareFile item APIs, maintains a directory ID cache, and handles ShareFile-specific timestamp and copy/move quirks.

## Important APIs, Types, and Functions

`Options` stores `root_folder_id`, upload cutoff/chunk size, endpoint, and encoding. `Fs` holds backend state: name/root, REST client, pacer, `dircache.DirCache`, upload buffer tokens, OAuth renewer, root ID, and the ShareFile timezone workaround location. `Object` stores remote path, metadata validity, size, modtime, item ID, and MD5. Key functions include `NewFs`, `readMetaDataForIDPath`, `FindLeaf`, `CreateDir`, `listAll`, `List`, `Put`, `PutUnchecked`, `purgeCheck`, `updateItem`, `move`, `Move`, `DirMove`, `Copy`, `Shutdown`, and object methods for hash, metadata, open, update, and remove.

## Control Flow

Initialization parses config, validates chunk size, creates an OAuth HTTP client, loads embedded `America/New_York` timezone data, resolves the root folder ID, initializes `dirCache`, and handles the common "root is actually a file" case by returning the parent `Fs` with `fs.ErrorIsFile`. Metadata reads go through directory-cache path resolution followed by `/Items(...)/ByPath` or `/Items(...)`. Listing reads `/Children` and converts folders to `fs.Dir` entries and files to `Object`s. Uploads create/find the parent folder and delegate object writes to `Object.Update`, which chooses normal or large upload behavior. Moves use a multi-step rename/move helper to avoid a ShareFile API overwrite bug. Copy may copy via a temporary folder because the API cannot rename while copying.

## State and Persistence Behavior

Runtime state includes cached directory IDs, cached upload buffers sized by `--transfers`, OAuth refresh state, and object metadata. Persistent configuration can include endpoint, OAuth token fields, root folder ID, and upload options. The backend stores no local data beyond config and embedded timezone data.

## Dependencies and Integration Points

It depends on `backend/sharefile/api`, rclone `fs`, `configstruct`, OAuth helpers, `dircache`, `encoder`, `pacer`, `random`, and `rest`. It implements rclone optional interfaces including hash reporting, purge, move, dir move, copy, directory cache flush, and shutdown. `upload.go` supplies the large-upload machinery used by `Object.Update`.

## Risks and Edge Cases

The backend contains explicit comments for ShareFile API bugs: patched modtimes are interpreted in Eastern time and only set to second precision, rename plus move can overwrite source-directory names, and copy cannot rename atomically. `Put` ignores open options when creating a missing object. Large uploads depend on buffer-token invariants and correct chunk sizes. `listAll` is non-paginated in this file, so very large folders depend on ShareFile API behavior. `Shutdown` assumes `tokenRenewer` is non-nil. Errors are parsed from JSON when possible but may include raw body text.

## Test Signals

`sharefile_test.go` runs rclone integration tests against `TestSharefile:` and exposes upload chunk/cutoff setters. Important signals include normal and chunked uploads, MD5 verification, server-side copy/move/dir move, directory cache invalidation, purge refusal for non-empty directories, timestamp precision, and root-as-file behavior.
