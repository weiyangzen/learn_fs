## sources/user-network-fs/gcsfuse/internal/locker/locker.go

### Purpose
`locker.go` provides a `sync.Locker` factory with optional invariant checking and deadlock debugging wrappers.

### Important APIs, Types, And Functions
Globals `EnableInvariantsCheck` and `EnableDebugMessages` enable wrappers before lockers are created. `Locker` aliases `sync.Locker`. `New` returns a base mutex optionally wrapped by `checker` and/or `debugger`. `checker.Lock/Unlock` call a supplied invariant function. `debugger.Lock/Unlock` track the holder stack and emit a delayed trace log after five seconds.

### Control Flow
`New` constructs a `sync.Mutex`, wraps it in `checker` if invariant checks are enabled, then wraps the result in `debugger` if debug messages are enabled. A debug lock captures the current goroutine stack after acquiring the mutex and starts a timer; unlock clears holder state, stops the timer, and unlocks the underlying locker.

### State, Persistence, And Dependencies
State is per-locker wrapper state plus package-level feature flags. There is no persistent storage. Dependencies include `runtime.Stack`, `time.AfterFunc`, `sync`, and the logger package.

### Integration Points
Internal packages can opt into invariant checks around lock-protected state and deadlock diagnostics globally. The logger dependency means debug output follows the global logging configuration and level.

### Risks
Feature flags are unsynchronized globals and are documented as needing to be set before creating lockers. `debugger` fields are not protected outside the lock lifecycle, and timer callbacks read `holder` asynchronously, so diagnostics are best-effort. `timer.Stop` return value is ignored, so a callback may already be running while unlock proceeds.

### Test Signals
No direct tests are in this shard. Useful tests would cover wrapper ordering, invariant invocation on lock/unlock, timer emission with a fake clock or short interval, and no panic when unlock races with timer execution.
