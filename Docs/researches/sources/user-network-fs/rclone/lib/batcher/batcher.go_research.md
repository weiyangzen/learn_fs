
# sources/user-network-fs/rclone/lib/batcher/batcher.go

Purpose: generic batching engine for grouping many item commits into fewer backend/API calls.

Important APIs/types/functions: `Options` configures mode, size, timeout, max size, and defaults. `CommitBatchFn[Item, Result]` is the user callback. `Batcher[Item, Result]` manages channels, async mode, shutdown, atexit registration, and waitgroup. Public methods are `New`, `Batching`, `Shutdown`, and `Commit`.

Control flow: `New` validates options, resolves defaults for `sync`, `async`, or `off`, creates buffered input channel, and starts `commitLoop` if active. `Commit` sends a request and either waits for a response in sync mode or returns immediately in async mode. `commitLoop` commits when batch size is reached, idle timeout fires, or shutdown occurs. `commitBatch` invokes the user callback with parallel results/errors arrays and distributes per-item responses.

State/persistence: in-memory pending request queue. Active batchers register `Shutdown` with `atexit` to flush on process exit.

Dependencies/integration: uses rclone config for default sync batch size, logging, fatal retry error wrapping, and `atexit`.

Risks: async mode cannot report per-item commit failures to callers. `Commit` sends to `b.in` without selecting on context cancellation, so a blocked channel can block the caller. User callback must fill result/error slices correctly.

Test signals: `batcher_test.go` covers construction validation, batch commit, failure propagation, shutdown, and async behavior.
