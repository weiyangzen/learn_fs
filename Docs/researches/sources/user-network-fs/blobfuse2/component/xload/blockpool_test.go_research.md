## sources/user-network-fs/blobfuse2/component/xload/blockpool_test.go

Purpose: Tests block pool sizing, block checkout/release, usage accounting, and full exhaustion.

Important APIs and flow: `TestBlockPoolAllocate` validates invalid inputs and a single-block pool. `TestBlockPoolGetRelease` checks priority and regular checkout/release on a five-block pool. `TestBlockPoolUsage` verifies usage percentages after one and two checkouts in a ten-block pool. `TestBlockPoolBufferExhaution` checks that ten priority checkouts consume the full pool and return to empty usage after release.

State and dependencies: Tests use `context.TODO()` and real mmap-backed blocks; each pool is terminated to unmap buffers.

Risks and test signals: Tests do not cover context cancellation, concurrent waiters, release after terminate, or regular checkout when only priority capacity exists. They establish basic invariants but not race safety under xload's live pipeline.
