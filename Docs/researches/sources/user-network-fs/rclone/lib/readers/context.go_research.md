# sources/user-network-fs/rclone/lib/readers/context.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/context.go -->
## sources/user-network-fs/rclone/lib/readers/context.go

Purpose: wraps an `io.Reader` so reads fail promptly when a context is canceled or reaches a deadline.

Important APIs and control flow: `NewContextReader(ctx, r)` returns a `contextReader`. `Read(p)` first checks `ctx.Err()` and returns that error with zero bytes when set; otherwise it delegates to the underlying reader.

State, dependencies, and integration: state is the context and underlying reader. Dependencies are `context` and `io`. This wrapper integrates with long-running transfer reads where cancellation should be observed before attempting more I/O.

Risks and test signals: cancellation is only checked before each underlying `Read`; a blocking underlying read cannot be interrupted by this wrapper alone. The paired test verifies normal pattern-reader output and post-cancel `context.Canceled`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/context.go -->
