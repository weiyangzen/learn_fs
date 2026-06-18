# sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter.go -->
## sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter.go

Purpose: provides a context-carried accumulator for server-side and other transfers that still need stats accounting.

Important APIs and control flow: `New(ctx, add)` creates a `TransferAccounter`, stores it in a derived context, and returns both. `Start` marks the accounter started. `Started` reports the flag. `Add(n)` calls the supplied `add` function and atomically increments `total`. `Reset()` reverses all accounted bytes by adding the negative total only if started. `Get(ctx)` returns the context accounter or a global no-op accounter when absent or ctx is nil.

State, dependencies, and integration: state includes a caller-provided add callback, atomic total, and non-atomic started flag. It depends on `context` and `sync/atomic`. Integration is through contexts passed along transfer operations.

Risks and test signals: `started` is not atomic, so concurrent `Start`/`Started` calls need external ordering. `Reset` does not clear `total` directly; it relies on `Add(-total)` to bring the atomic total back to zero. The global `nullAccounter` can have `started` set by tests/callers, which is harmless for no-op adds but shared state. Tests cover creation, start, add/reset, context lookup, nil/missing fallback, and no-op behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter.go -->
