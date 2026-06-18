# sources/storage-engines/pebble/internal/base/directory_lock.go

Purpose: Provides `DirLockSet`, `DirLock`, and `LockDirectory` for acquiring Pebble database directory locks through the VFS `LOCK` file. It lets callers pre-acquire a lock and pass it through open paths while preserving a small reference-count protocol.

APIs and types: `DirLockSet.String`, `Close`, and `AcquireOrValidate` manage a list of acquired locks. `LockDirectory` calls `fs.Lock(MakeFilepath(... FileTypeLock ...))` and returns a `DirLock`. `DirLock.refForOpen`, `Refs`, `Close`, and `pathMatches` implement validation and lifecycle.

Control flow and state: `AcquireOrValidate` either validates a pre-acquired lock against `dirname`, increments its ref count from 1 to 2, and records it, or acquires a new VFS lock. `DirLock.Close` atomically decrements refs; only the transition to zero closes the underlying `io.Closer`. `DirLockSet.Close` combines errors while closing all held locks and clears the slice.

Persistence and dependencies: The persistent artifact is the filesystem `LOCK` file lock acquired through `vfs.FS`; path construction depends on `filenames.go`. `pathMatches` deliberately uses `os.Stat` and `os.SameFile` outside VFS to handle relative paths and symlinks.

Integration points: Used by DB open/options code to prevent concurrent opens and to widen the critical section around setup. Invariant finalizers catch leaked locks when invariants are enabled.

Risks: Ref counts must stay in the expected 0/1/2 range. Closing too early can release an active DB lock; reusing a lock already opened by another DB returns an error. `pathMatches` is less portable for non-local VFS implementations because it bypasses VFS.

Test signals: No paired test in this subset, but `Refs` exists for tests and invariant finalizers provide leak detection in invariant builds.
