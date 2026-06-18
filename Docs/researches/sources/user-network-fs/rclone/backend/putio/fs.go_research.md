# sources/user-network-fs/rclone/backend/putio/fs.go

## Purpose
Put.io filesystem implementation: constructs OAuth client, dircache and SDK client; implements directory operations, TUS upload, server-side copy/move, quota and cleanup.

## Important APIs, Types, And Functions
Important surface: Fs, NewFs, CreateDir, FindLeaf, List, Put, PutUnchecked, createUpload, sendUpload, transferChunk, Copy, Move, DirMove, About, CleanUp.

## Control Flow
NewFs configures OAuth and file-root handling. Upload creates a TUS resource then PATCHes 48 MiB repeatable chunks, resolving offset mismatches with HEAD. Copy uses a temporary suffix before overwrite/rename.

## State And Persistence
remote files, folders, upload sessions, trash, dircache, OAuth config, transient upload locations.

## Dependencies And Integration Points
go-putio SDK, rclone oauth/fshttp/dircache/pacer/readers/hash.

## Risks And Test Signals
Risks and useful test signals: upload session loss, offset mismatch complexity, atoi panic on invalid IDs, copy overwrite sequencing, direct upload endpoint behavior.
