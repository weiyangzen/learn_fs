# sources/storage-engines/raft-engine/src/env/default.rs

## Purpose
Provides the default filesystem implementation and a `LogFile` adapter that turns shared low-level log file handles into standard `Read`, `Write`, `Seek`, and `WriteExt` objects.

## Important APIs, Types, And Functions
`LogFile` wraps `Arc<LogFd>` plus an offset. It implements `Write`, `Read`, `Seek`, and `WriteExt`. `DefaultFileSystem` implements `FileSystem` with `create`, `open`, `delete`, `rename`, `new_reader`, and `new_writer`.

## Control Flow
Reads and writes delegate to offset-based `LogFd` operations and advance the logical offset. `Seek` updates the offset from start/current/end positions. `truncate` delegates to the handle and resets offset. `allocate` delegates to the handle. Filesystem operations create/open/delete/rename underlying files and wrap handles as readers or writers. Failpoints inject zero writes and I/O errors for tests.

## State And Persistence Behavior
`LogFile` tracks only an in-memory offset; durable behavior comes from `LogFd` write, truncate, allocate, and sync operations. Delete removes physical files. Rename is used for file reuse and log movement.

## Dependencies And Integration Points
Depends on `env::FileSystem`, `Handle`, `Permission`, `WriteExt`, platform-specific `LogFd`, and failpoints. File pipe log readers/writers are built on this abstraction.

## Risks And Edge Cases
Offset arithmetic for `SeekFrom::Current` and `SeekFrom::End` casts signed values to `usize`; invalid negative seeks would wrap if callers misuse it. Failpoint zero writes validate upper layers. `flush` is a no-op because durability is explicit through handle sync.

## Test Signals
Failpoint-driven tests in the engine and file log layers exercise create/open/read/write/seek/truncate/allocate errors and zero writes.
