# sources/user-network-fs/rclone/lib/readers/limited.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/limited.go -->
## sources/user-network-fs/rclone/lib/readers/limited.go

Purpose: combines `io.LimitedReader` with `io.Closer` so callers can impose a byte limit while retaining close semantics.

Important APIs and control flow: `NewLimitedReadCloser(rc, limit)` returns `rc` unchanged for negative limits; otherwise it returns `*LimitedReadCloser` with an `io.LimitedReader{R: rc, N: limit}` and the original closer. `Close()` closes the underlying closer, but if close returns an error after all limited bytes were read (`N == 0`), it logs and suppresses that error.

State, dependencies, and integration: state is the embedded limited reader and closer. It depends on `io` and rclone `fs` logging. It integrates with partial-response readers where an underlying stream may complain on close even after the caller read exactly the intended content.

Risks and test signals: suppressing close errors when `N == 0` is a deliberate policy that could hide transport issues after complete reads. There is no direct test in the requested set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/limited.go -->
