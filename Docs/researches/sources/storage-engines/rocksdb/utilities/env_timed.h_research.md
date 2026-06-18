# sources/storage-engines/rocksdb/utilities/env_timed.h

## Purpose
This header declares `TimedFileSystem`, the FileSystem wrapper that instruments filesystem operation latency for PerfContext.

## Important APIs, Types, and Functions
The class derives from `FileSystemWrapper`, defines class name `TimedFS`, and overrides file-open, directory, metadata, delete/create, rename/link, lock/unlock, and logger creation methods.

## Control Flow
The header lists all operations that receive timing in the implementation. Construction wraps an existing shared `FileSystem`.

## State and Persistence Behavior
`TimedFileSystem` stores only the base filesystem inherited through `FileSystemWrapper`. It does not persist data or counters itself.

## Dependencies and Integration Points
It depends on RocksDB's `file_system.h`. Public helper declarations are implemented in the `.cc` file and used by `NewTimedEnv`.

## Risks and Edge Cases
The class does not wrap returned file objects, so per-read/write timing must come from other instrumentation. Any new FileSystem APIs added later will not be timed unless explicitly overridden.

## Test Signals
Compile coverage and `env_timed_test.cc` confirm basic construction and at least one timer. A comprehensive test would exercise each overridden method with PerfContext enabled.
