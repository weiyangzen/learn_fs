# sources/user-network-fs/rclone/lib/readers/repeatable_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/repeatable_test.go -->
## sources/user-network-fs/rclone/lib/readers/repeatable_test.go

Purpose: validates `RepeatableReader` caching and seek rules.

Important APIs and control flow: `TestRepeatableReader` reads an entire buffer, checks EOF, seeks back to start and rereads, checks partial sequential reads, verifies seeking past cache, negative seek, and invalid whence errors, then performs current/end-relative seeks and reads a slice spanning cached and newly read data.

State, dependencies, and integration: dependencies are `bytes`, `io`, `testing`, and testify. The test uses small fixed data to make cache positions clear.

Risks and test signals: covers essential cache/seek semantics. It does not test size-limited constructors, buffer-backed constructors, or concurrency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/repeatable_test.go -->
