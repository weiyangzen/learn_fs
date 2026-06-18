<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/benchmarks.go -->
# sources/sync-backup/restic/internal/backend/test/benchmarks.go

## Purpose
Provides reusable backend benchmark methods for load and save performance.

## Important APIs, Types, And Functions
saveRandomFile, remove, BenchmarkLoadFile, BenchmarkLoadPartialFile, BenchmarkLoadPartialFileOffset, and BenchmarkSave are important.

## Control Flow
Benchmarks create/open a backend, save random pack data, repeatedly load full or partial contents into buffers, compare bytes, and remove data as needed.

## State And Persistence Behavior
Persists temporary benchmark data through the backend under test and removes it afterwards.

## Dependencies And Integration Points
Depends on backend.Backend, restic.Hash, internal/test random data, context, bytes/io.

## Risks And Edge Cases
Benchmarks may be expensive for remote backends; MinimalData in suites can reduce test sizes elsewhere but these benchmark sizes are fixed.

## Test Signals
Used by backend-specific Benchmark* entry points.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/benchmarks.go -->
