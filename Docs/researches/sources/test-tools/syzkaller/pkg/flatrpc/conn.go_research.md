# sources/test-tools/syzkaller/pkg/flatrpc/conn.go

Purpose: `conn.go` implements size-prefixed FlatBuffers RPC transport over `net.Conn`, plus a TCP server wrapper and defensive parsing for executor messages.

Important APIs/types/functions: `Serv`, `Listen`, `Serv.Serve`, and `Serv.Close` manage server sockets. `Conn`, `NewConn`, `Close`, and `RemoteAddr` wrap connections. Generic `Send`, `Recv`, and `Parse` serialize object-API messages and unpack raw FlatBuffers messages. Verification helpers include `verify`, `verifyExecutorMessage`, and `verifyExecResult`. `statSent` and `statRecv` track traffic.

Control flow and state: server `Serve` accepts connections until listener close, runs handlers in an errgroup, closes connections on context cancellation, and treats non-temporary accept errors as fatal. `Send` is mutex-protected for concurrent writers and reuses a FlatBuffers builder. `Recv` is single-reader only; it compacts leftover buffered bytes, reads a 4-byte size prefix, rejects messages over 64 MiB, reads the full message, and parses the body. `Parse` recovers panics from corrupted FlatBuffers before unpacking.

Dependencies and integration: it depends on generated flatrpc raw types, FlatBuffers Go runtime, syzkaller stat/log packages, and errgroup. Executor verification limits allocation risk from untrusted test-machine data.

Risks: received object pointers are valid only until the next receive because buffers are reused. The receive path is not goroutine-safe. Verification currently special-cases executor messages only. Tests and fuzzing in `conn_test.go` cover round-trips and corrupted input resilience.
