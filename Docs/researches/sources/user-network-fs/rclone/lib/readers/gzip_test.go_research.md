# sources/user-network-fs/rclone/lib/readers/gzip_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/gzip_test.go -->
## sources/user-network-fs/rclone/lib/readers/gzip_test.go

Purpose: tests gzip decompression and close propagation for `NewGzipReader`.

Important APIs and control flow: the test compresses random test data into a buffer, wraps it with a custom `checkClose` read closer, reads all decompressed data through `NewGzipReader`, compares it to the original string, then closes the gzip reader and asserts the underlying closer was called.

State, dependencies, and integration: dependencies include `compress/gzip`, `bytes`, `io`, `lib/random`, and testify. The custom closer records state in a boolean.

Risks and test signals: it covers the happy path and close propagation, but not invalid gzip input or close-error precedence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/gzip_test.go -->
