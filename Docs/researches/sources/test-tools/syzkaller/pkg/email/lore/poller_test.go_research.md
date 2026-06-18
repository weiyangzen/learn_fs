# sources/test-tools/syzkaller/pkg/email/lore/poller_test.go

Purpose: `poller_test.go` validates `Poller` behavior against a local test git archive.

Important tests: `TestPoller` builds an archive with old and recent messages, verifies first-poll initialization plus lookback filtering, checks root resolution across replies, then adds a later reply and an own-email message. `TestPollerLoop` creates a cyclic ancestry pair and verifies no message is emitted. `TestPollerDateSanitization` confirms future-dated email headers are clamped to commit date.

Control flow and state: tests use `NewTestLoreArchive` to create commits with controlled dates, a buffered output channel for polled messages, and injected `now` functions. They call `Poll` directly rather than relying on ticker timing.

Dependencies and integration: tests cross the vcs test repo helper, archive reader, poller initialization, raw email parsing, and root-resolution logic.

Risks/test gaps: tests do not exercise network failures, git poll failures, context cancellation during channel send, or `Loop` retry logging. They give good coverage of stateful polling and ancestry correctness.
