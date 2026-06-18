# sources/user-network-fs/rclone/lib/pacer/tokens_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/tokens_test.go -->
## sources/user-network-fs/rclone/lib/pacer/tokens_test.go

Purpose: unit-tests the simple channel-backed `TokenDispenser` implementation.

Important APIs and control flow: `TestTokenDispenser` constructs a dispenser with five tokens, asserts the buffered channel length is five, calls `Get`, asserts length drops to four, calls `Put`, and asserts length returns to five.

State, dependencies, and integration: the test reaches into the unexported `tokens` channel because it is in package `pacer`, so it validates implementation state directly rather than using only public behavior. It depends on `testing` and `stretchr/testify/assert`.

Risks and test signals: the test confirms basic accounting but not blocking behavior, deadlock scenarios, over-release behavior, or zero/negative sizes. It is a smoke test for fixed-capacity channel initialization and one acquire/release cycle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/tokens_test.go -->
