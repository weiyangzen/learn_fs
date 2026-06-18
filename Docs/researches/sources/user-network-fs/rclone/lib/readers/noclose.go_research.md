# sources/user-network-fs/rclone/lib/readers/noclose.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noclose.go -->
## sources/user-network-fs/rclone/lib/readers/noclose.go

Purpose: hides `io.Closer` from an `io.Reader` so downstream code such as `http.NewRequest` cannot upgrade and close the original body unexpectedly.

Important APIs and control flow: `NoCloser(in)` returns nil unchanged, returns `in` unchanged when it does not implement `io.Closer`, and otherwise wraps it in an unexported `noClose` that exposes only `Read`. `noClose.Read` delegates directly to the underlying reader.

State, dependencies, and integration: state is a single underlying reader. It depends only on `io`. The REST client uses this wrapper when constructing request bodies.

Risks and test signals: callers that actually need close propagation must not use this wrapper. The test covers nil, non-closer pass-through, closer hiding, and delegated read errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noclose.go -->
