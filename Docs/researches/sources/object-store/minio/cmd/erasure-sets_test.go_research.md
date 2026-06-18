<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-sets_test.go -->
# sources/object-store/minio/cmd/erasure-sets_test.go

## Purpose
Unit and benchmark coverage for erasure-set hashing and basic set initialization. It protects object placement compatibility and verifies that a formatted endpoint set can be wrapped as an `erasureSets` object layer.

## Important APIs, types, and functions
- `BenchmarkCrcHash` and `BenchmarkSipHash` measure placement hash performance for key sizes from 16 to 1024 bytes.
- `TestSipHashMod` and `TestCrcHashMod` assert fixed bucket indexes for representative object names, Unicode, paths, and raw bytes.
- `TestNewErasureSets` exercises endpoint parsing, `waitForFormatErasure`, parity calculation through `ecDrivesNoConfig`, and `newErasureSets`.
- `TestHashedLayer` constructs synthetic sets and asserts `getHashedSet` returns the expected set under legacy `CRCMOD`.

## Control flow
Hash tests feed table entries into `hashKey` with a fixed UUID and cardinality 200, then separately assert `-1` for invalid cardinality or unknown algorithms. Initialization allocates 16 temporary disk paths, checks invalid `waitForFormatErasure` calls, formats disks, creates a `PoolEndpoints` wrapper, computes default parity, and initializes the erasure set layer. `TestHashedLayer` uses pointer identity to ensure object names map to stable set instances.

## State and persistence behavior
Tests create temporary disk paths and format metadata under them through the normal erasure formatting path. No long-lived state is intended; cleanup is via deferred `os.RemoveAll`. The fixed `testUUID` makes SipHash outputs deterministic.

## Dependencies and integration points
The tests use endpoint parsing, filesystem-backed storage setup, format waiting, parity lookup, erasure-set construction, and global test temp directory helpers. They are tightly coupled to placement algorithms in `erasure-sets.go`.

## Risks and edge cases
The expected hash indexes are compatibility fixtures; a legitimate algorithm change requires an explicit migration story. Initialization covers a single local 16-drive setup and does not validate reconnect, multi-pool, distributed lockers, or heal-format behavior.

## Test signals
Signals are exact hash outputs, exact invalid-argument errors from format waiting, successful `newErasureSets`, and pointer-equality mapping for legacy hashed sets. Benchmarks provide allocation/performance regression signals for hashing and do not assert behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-sets_test.go -->
