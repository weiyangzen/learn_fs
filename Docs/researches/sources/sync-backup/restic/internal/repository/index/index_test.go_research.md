## sources/sync-backup/restic/internal/repository/index/index_test.go

Purpose: comprehensive tests and benchmarks for `Index` serialization, lookup, grouping, allocation, and performance.

Important tests/helpers: `TestIndexSerialize` builds mixed compressed/uncompressed entries, encodes/decodes, verifies lookups and final IDs. `TestIndexSize` checks count and serialized size. `docExampleV1`/`docExampleV2`, `exampleTests`, and `TestIndexUnserialize` verify design-document JSON compatibility and `uncompressed_length`. `listPack` collects blobs for one pack. `createRandomIndex` and `NewRandomTestID` build large benchmark fixtures. Benchmarks cover decode, parallel decode, encode, hash lookup, allocation, and parallel allocation. `TestIndexPacks`, `TestIndexHas`, `TestMixedEachByPack`, and `TestEachByPackIgnoes` verify pack sets, type-aware membership, mixed blob grouping, and blacklist behavior.

Control flow and state: tests exercise both mutable and finalized indexes, direct JSON decode, and iterator APIs. Benchmarks use deterministic random seeds for repeatability.

Dependencies and integration points: validates on-disk compatibility and performance-critical memory layout behavior used by repository operations.

Risks and test signals: strong coverage for core index behavior. It intentionally reaches large synthetic indexes in benchmarks, but most unit tests stay moderate in size. The typo in `TestEachByPackIgnoes` is cosmetic.
