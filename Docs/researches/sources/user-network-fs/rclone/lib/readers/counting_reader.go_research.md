# sources/user-network-fs/rclone/lib/readers/counting_reader.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/counting_reader.go -->
## sources/user-network-fs/rclone/lib/readers/counting_reader.go

Purpose: wraps an `io.Reader` and counts cumulative bytes successfully returned by `Read`.

Important APIs and control flow: `NewCountingReader(in)` returns `*CountingReader`. `Read(b)` delegates to `in.Read(b)`, adds `n` to an internal `uint64`, and returns the original `(n, err)`. `BytesRead()` exposes the total.

State, dependencies, and integration: state is the underlying reader and count. There is no synchronization, so it is for single-reader use or externally synchronized use. It depends only on `io`.

Risks and test signals: reads that return `n > 0` with an error still count those bytes, matching Go `io.Reader` convention. There is no direct test in this requested set, so behavior is simple but unverified here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/counting_reader.go -->
