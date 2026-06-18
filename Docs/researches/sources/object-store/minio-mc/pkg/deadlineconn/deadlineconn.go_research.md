## sources/object-store/minio-mc/pkg/deadlineconn/deadlineconn.go

Purpose: wraps `net.Conn` to set per-read and per-write deadlines immediately before each operation. Important APIs are `DeadlineConn`, `Read`, `Write`, `WithReadDeadline`, `WithWriteDeadline`, and `New`.

Control flow is simple: `Read` calls `setReadDeadline` when configured and delegates to the embedded connection; `Write` does the same for writes. State is the wrapped connection plus configured durations. Dependencies are `net` and `time`. Integration points are network clients needing idle-operation timeouts without changing callers that expect `net.Conn`. Risks include ignoring `SetReadDeadline`/`SetWriteDeadline` errors, data races if deadlines are mutated concurrently, and the deadline being relative to call start rather than total request lifetime. `deadlineconn_test.go` verifies read deadlines are refreshed across delayed reads.
