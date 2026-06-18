# sources/sync-backup/kopia/repo/manifest/manifest_manager_test.go

Purpose: integration and unit tests for manifest manager lifecycle, persistence, corruption handling, validation, and compaction.

Important APIs/types/functions: `TestManifest`, `TestManifestInitCorruptedBlock`, helper `addAndVerify`, `verifyItem`, `verifyMatches`, `newManagerForTesting`, `TestManifestInvalidPut`, `TestManifestAutoCompaction`, `TestManifestConfigureAutoCompaction`, `TestManifestAutoCompactionWithReadOnly`, and `BenchmarkLargeCompaction`.

Control flow: tests add labeled manifests, verify find/get before and after flush, reopen a second manager over the same storage, delete and compact, corrupt underlying packs, validate bad puts, and check compaction behavior at thresholds and under read-only storage.

State/persistence behavior: uses in-memory blob storage plus content managers to persist manifest contents and indexes between manager instances.

Dependencies/integration: exercises content manager, format options, encryption/hashing defaults, read-only wrapper, blobtesting data maps, and test logging.

Risks/test signals: catches subtle reload/compaction and corruption paths. Benchmark covers large compaction performance but is not a correctness gate in normal tests.
