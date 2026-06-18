# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxStruc.h

## Purpose
Defines all shared data structures, pool tags, global state, context layouts, and debug-tracing macros for the `ctx` minifilter sample.

## Pool Tags
- `CTX_STRING_TAG`
- `CTX_RESOURCE_TAG`
- `CTX_INSTANCE_CONTEXT_TAG`
- `CTX_FILE_CONTEXT_TAG`
- `CTX_STREAM_CONTEXT_TAG`
- `CTX_STREAMHANDLE_CONTEXT_TAG`

## Main Structures
- `CTX_GLOBAL_DATA`
  - Holds the registered `PFLT_FILTER`.
  - In checked builds, stores `DebugLevel`.

- `CTX_INSTANCE_CONTEXT`
  - Stores `PFLT_INSTANCE`.
  - Stores `PFLT_VOLUME`.
  - Stores `UNICODE_STRING VolumeName`.

- `CTX_FILE_CONTEXT`
  - Stores immutable `UNICODE_STRING FileName`.
  - No lock is included because the file name is set at creation and not modified.

- `CTX_STREAM_CONTEXT`
  - Stores `UNICODE_STRING FileName`.
  - Counts observed create, cleanup, and close events:
    - `CreateCount`
    - `CleanupCount`
    - `CloseCount`
  - Uses `PERESOURCE Resource` to protect mutable fields.

- `CTX_STREAMHANDLE_CONTEXT`
  - Stores `UNICODE_STRING FileName`.
  - Uses `PERESOURCE Resource` to protect mutable fields.

## Debug Support
Checked builds define trace flags for:
- errors
- load/unload
- instance lifecycle
- instance/file/stream/stream-handle context operations
- all tracked I/O

`DebugTrace(Level, Data)` maps to `DbgPrint` when the requested level intersects `Globals.DebugLevel`; in free builds it expands to no work.

## Research Notes
The file distinguishes three useful Filter Manager scopes:
- file context: immutable per file object/name snapshot
- stream context: mutable stream-level counters and name
- stream-handle context: mutable handle-level name state

This separation is the core teaching point of the `ctx` sample.
