# Research: sources/object-store/minio-mc/cmd/pipechan_test.go

## sources/object-store/minio-mc/cmd/pipechan_test.go

Purpose: tests and benchmarks `PipeChan` against regular buffered channels for event delivery correctness and throughput.

Important APIs and functions: `testPipeChan` sends `totalMsgs` `notify.EventInfo` values and verifies all arrive unchanged; `TestPipeChannel` checks `PipeChan(1000)` with 10,000 messages; `TestRegularChannel` runs the same harness on a normal channel; benchmark helpers compare regular and pipe channels at 1K, 10K, 100K, and 1M message counts.

Control flow: producer and consumer goroutines are coordinated with a wait group. The producer closes input when done; the consumer counts messages until output closes and records corruption.

State and persistence: test-only in-memory channel state.

Dependencies and integration: depends on `github.com/rjeczalik/notify` and the pipe channel implementation. Benchmarks provide performance expectations but are not assertions.

Risks and test signals: the tests validate delivery count and value identity for nil event info, but they do not test non-nil events, capacity edge cases, cancellation, or memory behavior under long-running watch workloads.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipechan_test.go -->
