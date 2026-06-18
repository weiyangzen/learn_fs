## sources/object-store/minio-mc/pkg/deadlineconn/deadlineconn_test.go

Purpose: integration-style unit test for `DeadlineConn` timeout behavior using a real local TCP listener and client.

Control flow starts a listener, accepts one TCP connection, wraps it, sets one-second read/write deadlines, reads `message one`, sleeps three seconds, reads `message two`, then writes a response. The client writes both messages and expects `messages received`. State is local sockets and a wait group. Dependencies are `net`, `io`, `bufio`, `sync`, and `testing`. The signal is specifically that read deadlines are reset before every read, so processing delays between reads do not permanently expire the connection. Risks include timing flakiness under extremely slow CI and no explicit negative timeout assertion.
