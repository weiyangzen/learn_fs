# sources/user-network-fs/rclone/lib/readers/context_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/context_test.go -->
## sources/user-network-fs/rclone/lib/readers/context_test.go

Purpose: confirms `NewContextReader` delegates reads while active and returns the context error after cancellation.

Important APIs and control flow: the test wraps a `NewPatternReader(100)` with a cancellable context, reads three bytes and checks `{0,1,2}`, cancels, then reads again and expects zero bytes plus `context.Canceled`.

State, dependencies, and integration: dependencies are `context`, `testing`, and testify. It indirectly depends on `pattern_reader.go` for deterministic input.

Risks and test signals: it verifies pre-read cancellation checks but not deadlines, already-canceled contexts at construction, or underlying read blocking behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/context_test.go -->
