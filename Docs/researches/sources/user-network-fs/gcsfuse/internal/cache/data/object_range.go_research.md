# sources/user-network-fs/gcsfuse/internal/cache/data/object_range.go

## Purpose
`ObjectRange` is a small data-transfer type representing a byte range within a GCS object. It is intended for cache/download coordination where start and end offsets need to travel together.

## Important APIs, Types, And Functions
The file defines one exported struct:

```go
type ObjectRange struct {
    Start int64
    End   int64
}
```

There are no methods, validation helpers, or constants.

## Control Flow And State
There is no control flow. The struct stores two signed offsets and leaves range semantics to callers.

## State And Persistence Behavior
The type is in-memory metadata only. It does not persist data or interact with files.

## Dependencies And Integration Points
It has no imports. Its package location makes it available to cache data, file, and downloader code that need object-range metadata.

## Risks And Edge Cases
Because the type does not define whether `End` is inclusive or exclusive and does not validate ordering or non-negativity, callers must document and enforce those invariants at use sites.

## Test Signals
No direct tests are listed for this file. Coverage is likely through consumers if any.
