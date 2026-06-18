<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/parallel_test.go -->
# sources/sync-backup/restic/internal/restic/parallel_test.go

## Purpose
Tests `ParallelRemove` against a mock unpacked-file remover and an atomic test counter.

## Important APIs and Control Flow
`mockRemoverUnpacked` provides two connections and injectable removal behavior; `NewTestID` creates deterministic IDs; `TestParallelRemove` table-drives successful deletes, remove failures, report failures, expected report IDs, and progress counts. The test collects removed IDs under synchronization where needed and checks that errors stop the errgroup while successful removals advance the counter.

## State, Persistence, Dependencies, and Integration
State is entirely test-local: ID sets, mutex/atomic counters, and error injections. It depends on `internal/errors` and core restic ID helpers.

## Risks and Test Signals
The suite gives useful concurrency-contract coverage but remains timing-light; it does not force high contention or verify exact scheduling order.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/parallel_test.go -->
