<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/queue_test.go -->
# Research: sources/user-network-fs/gcsfuse/common/queue_test.go

Purpose: unit tests for the generic linked-list queue implementation.

Important APIs/types/functions: tests call `NewLinkedListQueue[int]`, `Push`, `Peek`, `Pop`, `Len`, and `IsEmpty`, with testify assertions and panic checks.

Control flow: cases build queues, enqueue several integers, verify FIFO pop order, verify `Peek` leaves length unchanged, and assert that empty `Pop` and `Peek` panic.

State and persistence: all state is in-memory queue state scoped to each test; no external files or global state.

Dependencies: Go testing plus `github.com/stretchr/testify/assert` and `require`.

Risks: tests do not exercise concurrent access because the queue is intentionally unsynchronized. They also do not test pointer payload aliasing, but that is outside queue ownership.

Test signals: run `go test ./common -run LinkedListQueue`; failures indicate a FIFO invariant or panic-contract change.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/queue_test.go -->
