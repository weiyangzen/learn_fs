# sources/user-network-fs/s3fs-fuse/src/syncfiller.h

## Purpose
Defines `SyncFiller`, the thread-safe FUSE directory filler facade used to protect `fuse_fill_dir_t` calls and avoid repeated directory entries.

## Important APIs, Types, And Control Flow
`SyncFiller(void* buff, fuse_fill_dir_t filler)` establishes the callback target. `Fill` handles one named entry with optional stat and offset. `SufficiencyFill` handles a vector of fallback names. Copy and move operations are deleted because the class owns synchronization state tied to a FUSE buffer.

## State And Persistence
The class stores `filler_lock`, the opaque FUSE buffer, the filler callback, and a `filled` set. State is valid only for a directory-fill operation and should not persist beyond the owning readdir request.

## Dependencies And Integration Points
Includes STL mutex/vector/set/string and `s3fs.h` for FUSE definitions and `S3FS_FUSE_FILL_DIR_DEFAULTS`. It is a direct bridge between s3fs listing logic and libfuse.

## Risks And Test Signals
The header exposes no way to clear `filled`, so one object should be used per listing. Callback and buffer lifetime are external. Signals are mostly integration-level: directory listing, recursive removal, implicit directory discovery, and concurrent directory update tests.
