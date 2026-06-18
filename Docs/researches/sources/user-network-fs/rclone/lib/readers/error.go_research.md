# sources/user-network-fs/rclone/lib/readers/error.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/error.go -->
## sources/user-network-fs/rclone/lib/readers/error.go

Purpose: provides a tiny `io.Reader` implementation that always fails with a configured error.

Important APIs and control flow: `ErrorReader{Err: err}` implements `Read(p)` by returning `(0, Err)` without touching `p`.

State, dependencies, and integration: state is only the stored error. It has no imports. It is useful for tests or adapter paths that need an `io.Reader` placeholder representing a prior failure.

Risks and test signals: if `Err` is nil, `Read` returns `(0, nil)`, which can cause callers to spin because it violates the useful progress convention. The paired test covers a non-nil error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/error.go -->
