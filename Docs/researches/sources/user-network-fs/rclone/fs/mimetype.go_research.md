# sources/user-network-fs/rclone/fs/mimetype.go

## Purpose
`mimetype.go` provides MIME type detection helpers for rclone directory entries and augments Go's built-in extension database with common media extensions on platforms lacking a rich `mime.types`.

## Important APIs, types, and functions
Exports are `MimeTypeFromName`, `MimeType`, and `MimeTypeDirEntry`. The package `init` registers fallback MIME types for audio, image, video, and subtitle extensions when `mime.TypeByExtension` lacks them.

## Control flow
At init, each comma-separated extension is registered only if Go has no type for it. `MimeTypeFromName` checks `path.Ext` and returns `application/octet-stream` unless the result contains `/`. `MimeType` prefers an object's `MimeTyper` implementation when non-empty, then falls back to filename. `MimeTypeDirEntry` returns `inode/directory` for directories and delegates to `MimeType` for objects.

## State and persistence behavior
The process-global MIME extension table is mutated during package init. No files are read or written by this code.

## Dependencies and integration points
It depends on Go `mime`, `path`, and rclone interfaces `DirEntry`, `Object`, `Directory`, and `MimeTyper`. Metadata mapping and backend uploads use these helpers to infer content type.

## Risks and edge cases
MIME type registration is global and can affect other packages in-process. Extension matching is filename-based and not content-sniffing. If a `MimeTyper` returns an invalid but non-empty type, this helper trusts it.

## Test signals
No direct test is in this subset. Metadata mapper tests indirectly assert `file.txt` produces `text/plain; charset=utf-8`.

Source-read signal: reviewed complete local file (81 lines). Functions/methods observed: `init`, `MimeTypeFromName`, `MimeType`, `MimeTypeDirEntry`.
