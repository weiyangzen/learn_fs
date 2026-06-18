## sources/user-network-fs/gcsfuse/internal/locker/rw_locker.go

### Purpose
`rw_locker.go` extends the locker factory pattern to read/write locks, adding optional invariant checks and writer-only deadlock diagnostics around `sync.RWMutex`.

### Important APIs, Types, And Functions
`RWLocker` embeds `sync.Locker` and adds `RLock`/`RUnlock`. `NewRW` builds a base `sync.RWMutex` and optionally wraps it in `rwChecker` and `rwDebugger`. `rwChecker` validates invariants after acquiring and before releasing both read and write locks. `rwDebugger` tracks only write locks with delayed trace logging.

### Control Flow
Construction mirrors `locker.New`. Write-lock acquisition captures a goroutine stack and starts a five-second timer after the lock is obtained; unlock clears and stops it. Read locks simply delegate in the debug wrapper, while the checker wrapper still invokes the invariant function for readers.

### State, Persistence, And Dependencies
State is in wrapper fields and global flags shared with `locker.go`. There is no persistent state. Dependencies are `sync`, `runtime`, `time`, and logger.

### Integration Points
Packages using read-mostly state can use `NewRW` to centralize invariant checks without changing call sites to direct `sync.RWMutex`.

### Risks
Read-lock deadlocks are intentionally not diagnosed. The same global flag and timer race caveats as `locker.go` apply. Running invariant checks while holding read locks may be expensive or may require the invariant function to avoid write-lock acquisition.

### Test Signals
No tests are present. Targeted tests should validate read/write invariant call counts, writer debug log behavior, and read-lock pass-through behavior under debug mode.
