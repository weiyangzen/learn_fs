# sources/test-tools/syzkaller/pkg/flatrpc/conn_test.go

Purpose: `conn_test.go` validates FlatRPC transport round-trips, provides a benchmark, and fuzzes corrupted receive data.

Important tests/functions: `TestConn` starts a local TCP server, exchanges `ConnectHello`, `ConnectRequest`, `ConnectReply`, and repeated `ExecutorMessage` values, then closes the server and checks handler completion. `BenchmarkConn` measures repeated request/reply cycles. `FuzzRecv` seeds a valid executor result, mutates size-prefixed byte streams through a socketpair, constrains memory with `debug.SetMemoryLimit`, skips large fuzz inputs, and repeatedly calls `Recv` until error.

Control flow and state: the test server runs `Serv.Serve` in a goroutine and uses generic `Send`/`Recv` with generated raw types. The fuzz test uses OS socketpairs to exercise real connection reads instead of direct parser calls.

Dependencies and integration: tests cover `Listen`, `Serve`, `NewConn`, `Send`, `Recv`, FlatBuffers packing/unpacking, and executor message verification. They depend on generated flatrpc types and `testify/assert`.

Risks/test gaps: concurrency of multiple simultaneous client connections and concurrent sends is not directly tested. Fuzzing focuses on executor messages and short inputs, but it directly targets the highest-risk corrupted-input path.
