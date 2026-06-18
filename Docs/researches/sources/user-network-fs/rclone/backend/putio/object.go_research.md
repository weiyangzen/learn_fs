# sources/user-network-fs/rclone/backend/putio/object.go

## Purpose
Put.io object implementation: handles object metadata lookup, CRC32 hash, MIME, modtime, direct download, update and removal.

## Important APIs, Types, And Functions
Important surface: Object, NewObject, newObjectWithInfo, readEntry, setMetadataFromEntry, Hash, Size, ID, MimeType, SetModTime, Open, Update, Remove.

## Control Flow
metadata lookup uses dircache then /child?name; Open obtains a storage URL and direct GETs with range headers; Update removes the old file and uploads replacement unless ignored filename regex matches

## State And Persistence
remote file metadata/content/type/timestamps; local cached putio.File and modtime.

## Dependencies And Integration Points
go-putio, rclone fs/hash/fserrors, direct HTTP.

## Risks And Test Signals
Risks and useful test signals: old object lost if replacement upload fails after remove, Open requires populated file, ignored files silently skip upload.
