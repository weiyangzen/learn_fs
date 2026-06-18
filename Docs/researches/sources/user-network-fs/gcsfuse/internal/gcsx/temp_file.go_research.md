## sources/user-network-fs/gcsfuse/internal/gcsx/temp_file.go

### Purpose
`temp_file.go` implements `TempFile`, a lazy temporary-file wrapper around initial object contents. It tracks the earliest byte offset that differs from the original source so sync code can decide whether an object can be appended or must be fully rewritten.

### Important APIs, Types, And Functions
`TempFile` exposes invariant checks, `io.ReadSeeker`, `io.ReaderAt`, `io.WriterAt`, `Truncate`, `Name`, `Stat`, `SetMtime`, and `Destroy`. `StatResult` reports `Size`, `DirtyThreshold`, and optional `Mtime`. Constructors are `NewTempFile`, `NewCacheFile`, and `RecoverCacheFile`. Internal state uses `fileIncomplete`, `fileComplete`, `fileDirty`, and `fileDestroyed`. Helpers include `ensure`, `ensureComplete`, and `minInt64`.

### Control Flow
New temp/cache files start incomplete with a source reader and an `os.File`; recovered cache files start complete with dirty threshold equal to file size. Reads, seeks, stats, writes, and truncates call `ensureComplete`, which copies source data into the backing file in at least 64 MiB chunks until EOF. EOF closes the source, marks the file complete, and sets `dirtyThreshold` to the copied size. Writes and truncates lower the dirty threshold to the write offset or truncation size, mark the file dirty, and set mtime from the injected clock. `Stat` seeks to end for size, so callers are warned that it may invalidate seek position.

### State, Persistence, And Dependencies
Persistent state is the backing anonymous/cache file and in-memory fields for state, dirty threshold, source reader, and mtime. `Destroy` closes and nils the file for anonymous cleanup. Dependencies include `fsutil.AnonymousFile`, `timeutil.Clock`, `os.File`, and standard I/O primitives.

### Integration Points
The syncer and file-cache paths use `TempFile.Stat()` to detect unchanged prefixes and mtimes. `Name` exposes the backing file path for cache-oriented callers. `RecoverCacheFile` integrates already existing cache files by treating them as fully loaded clean content.

### Risks
The type is explicitly not concurrency-safe. `ensure` ignores the `Seek` error in the incomplete branch, so a failing seek can leave `size` zero and return a later copy error or nil in unusual conditions. `SetMtime` does not change `dirtyThreshold` or `state`, allowing mtime-only updates. Because `Stat` changes the seek offset, callers must preserve position if needed.

### Test Signals
Existing tests cover initial stat, reads, writes, truncation, explicit mtime, dirty threshold updates, invariant checks around operations, and simulated clock behavior. Gaps include cache-file recovery, destroy-after-use errors, huge lazy copy chunking, source read errors other than EOF, and concurrent misuse.
