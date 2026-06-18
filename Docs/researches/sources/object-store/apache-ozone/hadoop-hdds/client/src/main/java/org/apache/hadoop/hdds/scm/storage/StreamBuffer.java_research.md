# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamBuffer.java

## Purpose
`StreamBuffer` is a thin wrapper around `ByteBuffer` used by the older streaming write commit watcher path.

## Important APIs and Types
It offers constructors from a whole buffer or a read-only slice defined by offset/length, `duplicate()`, `remaining()`, `position()`, `put(StreamBuffer)`, and `allocate(int)`.

## Control Flow
The slice constructor creates a read-only buffer view with adjusted position and limit. `put` copies from another wrapped buffer into this buffer. Commit watchers use `position()` to account acknowledged bytes.

## State and Persistence Behavior
State is only the wrapped `ByteBuffer`. No persistence occurs.

## Dependencies and Integration Points
Used by `StreamCommitWatcher` and streaming write-related code in the storage package. It is analogous to `ChunkBuffer` for paths that operate directly on `ByteBuffer`.

## Risks
The slice constructor stores a buffer with non-zero position; callers must understand that `remaining()` and `position()` reflect the view, not necessarily a standalone zero-based buffer. `put` mutates both destination and source wrapped buffer positions.

## Test Signals
No direct test surfaced in this subset; coverage is likely through streaming write tests if enabled.
