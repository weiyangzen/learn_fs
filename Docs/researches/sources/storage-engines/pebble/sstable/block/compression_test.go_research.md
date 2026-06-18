## sources/storage-engines/pebble/sstable/block/compression_test.go

Purpose: Randomized stress test for `TempBuffer` append/reset/release behavior and `PhysicalBlockMaker.Make` with Snappy compression and CRC32c checksums.

Important APIs/types/functions: `TestBufferRandomized` uses `PhysicalBlockMaker.Init`, `NewTempBuffer`, `TempBuffer.Append`, `Data`, `Size`, `Reset`, `Release`, and `PhysicalBlock.Release`.

Control flow: For 25 iterations, the test sometimes releases and recreates a temp buffer, then appends random byte slices until reaching a random aggregate size between 1 KiB and 4 MiB. It verifies the buffer size and trailing appended bytes after each append, then builds a physical SSTable data block and releases it.

State and persistence behavior: Exercises temporary in-memory buffer growth and physical block creation, not persisted files. Physical blocks include compressed data and trailer bytes, but the test does not decode them.

Dependencies and integration points: Uses `blockkind.SSTableData`, `SnappyCompression`, `ChecksumTypeCRC32c`, `math/rand/v2`, time seed, and `require`.

Risks: No seed control beyond logging; failures may need the logged seed. The test validates buffer integrity and allocation lifecycle but not checksum/decompression round-trip correctness.

Test signals: Good stress signal for large append paths, temp-buffer reuse, and interaction between temp buffers and physical block creation.
