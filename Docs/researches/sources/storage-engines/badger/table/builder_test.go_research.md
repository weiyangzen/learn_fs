# sources/storage-engines/badger/table/builder_test.go

## Purpose
This file tests SSTable builder output, table indexes, compression/encryption compatibility, bloom filters, empty builders, and builder performance.

## Important Tests and Benchmarks
- `TestTableIndex` writes 100,000 keys and verifies that index block offsets contain exactly the first key of each block across four option combinations: plain, encrypted, compressed, and compressed+encrypted.
- `TestInvalidCompression` opens a ZSTD-built table with correct and incorrect compression options and expects the incorrect option to fail.
- `TestBloomfilter` checks `DoesNotHave` with and without bloom filters in forward and reverse iteration.
- `TestEmptyBuilder` asserts an empty builder finishes to an empty byte slice.
- `BenchmarkBuilder` measures building 1.3M entries under no compression, encryption, Snappy, and multiple ZSTD levels.

## Control Flow and State Behavior
`TestTableIndex` mirrors the builder's own `shouldFinishBlock` decisions to track expected block first keys, then creates a table and reads the FlatBuffer index back for comparison. The test also checks key ID behavior in unencrypted mode and max version metadata.

Bloom tests build tables with and without filters, iterate all entries to verify present keys are never rejected, then probe an absent hash to confirm filters are active only when configured.

## Dependencies and Integration Points
The tests use `table.CreateTable`, `buildTestTable` from `table_test.go`, Badger options, FlatBuffer table indexes, protobuf data keys, Ristretto index cache for encryption, and `y` hashing/timestamp helpers.

## Risks and Edge Cases
The test reads indexes directly but does not independently parse raw SST bytes. Random file names in temp directories require cleanup via table close/remove. The invalid compression test reuses a table mmap and relies on open-time decode behavior to detect the mismatch.

## Test Signals
These tests provide strong format-level confidence for index offsets, encryption/index-cache requirements, compression option mismatches, bloom filter presence, and empty-output handling.
