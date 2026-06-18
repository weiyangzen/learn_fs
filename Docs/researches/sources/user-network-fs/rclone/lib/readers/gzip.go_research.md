# sources/user-network-fs/rclone/lib/readers/gzip.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/gzip.go -->
## sources/user-network-fs/rclone/lib/readers/gzip.go

Purpose: wraps `gzip.Reader` so closing the gzip stream also closes the underlying `io.ReadCloser`.

Important APIs and control flow: `NewGzipReader(in)` constructs a `gzip.Reader` over `in` and returns `*gzipReader`. `Close()` closes the gzip reader first and the underlying stream second; it returns the underlying close error if present, otherwise the gzip close error.

State, dependencies, and integration: `gzipReader` embeds `*gzip.Reader` and stores `in io.ReadCloser`. Dependencies are `compress/gzip` and `io`. This integrates with transfer paths that wrap compressed HTTP or file bodies and need deterministic resource cleanup.

Risks and test signals: if `gzip.NewReader` fails, the underlying input is not closed by this function; caller retains ownership. Error precedence favors the underlying stream close. The test verifies decompression and underlying close invocation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/gzip.go -->
