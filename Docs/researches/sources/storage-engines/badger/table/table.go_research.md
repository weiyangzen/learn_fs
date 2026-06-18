# sources/storage-engines/badger/table/table.go

## Purpose
This file implements loading, reading, caching, checksum verification, decryption, decompression, metadata access, and lifecycle management for Badger SSTable files.

## Important APIs, Types, and Functions
- `Options` configures table size, block size, bloom filters, checksum verification, compression, encryption, block/index caches, metrics, and allocator pool.
- `Table` wraps an mmap file, cheap index metadata, optional full index, table key bounds, file ID, checksum/index positions, refcount, and options.
- `CreateTable`, `OpenTable`, and `OpenInMemoryTable` create or load tables.
- Metadata methods include `MaxVersion`, `BloomFilterSize`, `UncompressedSize`, `KeyCount`, `OnDiskSize`, `CompressionType`, `Smallest`, `Biggest`, `ID`, `KeyID`, and `StaleDataSize`.
- `block`, `fetchIndex`, `readTableIndex`, `VerifyChecksum`, `DoesNotHave`, `KeySplits`, `ParseFileID`, `IDToFilename`, and `NewFilename` implement read and utility behavior.
- `Block` owns decoded block bytes, entry offsets, checksum, and refcount/freeing state.

## Control Flow and State Behavior
`CreateTable` finalizes a builder, mmaps a newly created file, copies build data, msyncs it, and opens the table. `OpenTable` validates filename ID, initializes refcount, reads table index/footer/checksum, initializes smallest and biggest keys, and optionally verifies checksums. `initIndex` reads footer checksum length, checksum, index length, and index bytes; verifies the index checksum; reads the FlatBuffer index; caches cheap metadata; and records whether a bloom filter exists.

For reads, `block` checks block cache, increments block refs safely, reads the block bytes, decrypts and decompresses as configured, parses checksum and entry offset metadata, verifies block checksums according to mode, and optionally admits the block to cache. `DecrRef` deletes cached blocks and the table file when the final reference drops. Encrypted tables do not retain `_index` directly and require an index cache.

## Dependencies and Integration Points
The table layer integrates with builder output, iterators, Ristretto block/index caches, level controller table lifecycle, manifest-created SST files, options, protobuf checksums, FlatBuffers, mmap files, and encryption/compression helpers.

## Risks and Edge Cases
Reference counting is critical: iterators, levels, and caches must not use deleted files or freed decompression buffers. Compression options must match the file; wrong options can produce decode/checksum errors. Encrypted workloads require `IndexCache`. `blockCacheKey` assumes IDs and indexes fit `uint32`. Corrupt metadata can panic in initialization paths, though recovery diagnostics are added for index crashes.

## Test Signals
`table_test.go` and `builder_test.go` cover opening, iteration, seek boundaries, bloom filters, checksum corruption, compression mismatch, large values, max version, concurrent `DoesNotHave`, and benchmarks.
