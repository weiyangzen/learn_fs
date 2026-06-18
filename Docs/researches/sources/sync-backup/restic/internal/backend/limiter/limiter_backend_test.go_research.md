<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter_backend_test.go -->
# sources/sync-backup/restic/internal/backend/limiter/limiter_backend_test.go

## Purpose
Tests rate-limited backend wrapping for Save and Load without depending on timing-sensitive throughput assertions.

## Important APIs, Types, And Functions
TestLimitBackendSave, TestLimitBackendLoad, randomBytes, and tracedReadWriteToCloser are the main helpers.

## Control Flow
Mock backends consume or return data while wrappers apply a static limiter. Load tests vary whether inner/outer readers expose WriterTo to ensure optimized copy paths still work.

## State And Persistence Behavior
No persisted state; random test data is in memory.

## Dependencies And Integration Points
Depends on mock backend, backend.NewByteReader, crypto/rand, and internal/test assertions.

## Risks And Edge Cases
The tests validate correctness, not actual bandwidth rate. Timing behavior is covered in static limiter tests.

## Test Signals
Strong regression signal for decorator semantics and data integrity.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter_backend_test.go -->
