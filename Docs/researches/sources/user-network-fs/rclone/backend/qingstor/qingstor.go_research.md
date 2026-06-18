# sources/user-network-fs/rclone/backend/qingstor/qingstor.go

## Purpose
QingStor backend: maps QingStor buckets/keys to rclone filesystem operations including bucket listing, object listing, copy, upload/download, cleanup, hashes and MIME.

## Important APIs, Types, And Functions
Important surface: Options, Fs, Object, qsServiceConnection, NewFs, List, ListR, Put, Copy, Mkdir, Rmdir, CleanUp, readMetaData, Open, Update, Remove, Hash.

## Control Flow
NewFs validates upload options and endpoint, creates SDK service, detects file roots by HEAD. Listing paginates buckets/objects; Update delegates to uploader; SetModTime copies object to itself for smaller objects.

## State And Persistence
remote buckets, objects, multipart uploads; local bucket cache and object metadata.

## Dependencies And Integration Points
yunify QingStor SDK, rclone bucket/list/fshttp/hash/encoder.

## Risks And Test Signals
Risks and useful test signals: unsupported build targets, endpoint parsing, SDK retry option not wired, multipart checksum/concurrency caveat, ETag MD5 ambiguity.
