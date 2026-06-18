<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/prefetch_block_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/block/prefetch_block_test.go

Purpose: tests `PrefetchBlock` behavior for buffered-read blocks.

Important APIs/types/functions: `PrefetchMemoryBlockTest`, `createPrefetchBlock`, `ReadAt`, `ReadAtSlice`, `SetAbsStartOff`, `AbsStartOff`, `AwaitReady`, `NotifyReady`, `IncRef`, `DecRef`, and `ReadFrom`.

Control flow: tests fill blocks, assert slice/copy reads and EOF handling, validate negative/out-of-bounds offsets, exercise one-shot readiness notification with cancellation and multiple waiters, verify ref-count panic cases, and feed readers with short, long, empty, partial, and erroring streams.

State and persistence: process-local mmap-backed buffers and goroutines/channels for readiness tests; no persistent state.

Dependencies: context cancellation, testify suite, and small helper readers.

Risks: asynchronous notification tests depend on goroutine scheduling. The suite does not exercise integration with the workerpool or FUSE callback lifetime.

Test signals: `go test ./internal/block -run PrefetchMemoryBlockTestSuite`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/prefetch_block_test.go -->
