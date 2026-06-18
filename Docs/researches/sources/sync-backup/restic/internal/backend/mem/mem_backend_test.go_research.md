<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mem/mem_backend_test.go -->
# sources/sync-backup/restic/internal/backend/mem/mem_backend_test.go

## Purpose
Runs the generic backend contract suite against the in-memory backend.

## Important APIs, Types, And Functions
newTestSuite, TestSuiteBackendMem, and BenchmarkSuiteBackendMem are the test entry points.

## Control Flow
The suite builds a mem factory and executes shared tests/benchmarks.

## State And Persistence Behavior
State is in-memory through MemoryBackend.NewFactory.

## Dependencies And Integration Points
Depends on backend/mem and backend/test Suite.

## Risks And Edge Cases
Does not test process restart durability, by design.

## Test Signals
Good signal that the memory backend satisfies the backend interface.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mem/mem_backend_test.go -->
