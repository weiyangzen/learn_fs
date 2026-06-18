# sources/user-network-fs/rclone/backend/quatrix/quatrix.go

## Purpose
Quatrix backend: maps Quatrix file APIs to rclone operations with dynamic chunked uploads, metadata, delete, copy, move and quota.

## Important APIs, Types, And Functions
Important surface: Options, Fs, Object, fileID, metadata, setMTime, deleteObject, Copy, Move, DirMove, uploadSession, dynamicUpload, finalize.

## Control Flow
NewFs configures bearer auth, custom transport, root ID and dircache. Upload creates/modifies a session, sends Content-Range chunks sized by UploadMemoryManager, finalizes with mtime, and deletes partial files on error.

## State And Persistence
remote file IDs, upload keys, trash/hard delete, quota; local dircache, object metadata, memory manager.

## Dependencies And Integration Points
quatrix/api, rclone rest/fshttp/dircache/multipart/pacer.

## Risks And Test Signals
Risks and useful test signals: unknown-size upload loop, memory pressure, hash returns empty nil, project folder filtering, overwrite semantics.
