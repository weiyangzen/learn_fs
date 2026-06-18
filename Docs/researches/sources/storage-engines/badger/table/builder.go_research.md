# sources/storage-engines/badger/table/builder.go

## Purpose
This file builds Badger SSTable files. It accumulates sorted key/value pairs into prefix-compressed blocks, optionally compresses and encrypts blocks, writes per-block checksums, builds a FlatBuffer table index with bloom filters and table metadata, and returns either bytes or structured build data for file creation.

## Important APIs, Types, and Functions
- `Builder` owns allocator state, current block, block list, size counters, key hashes, options, max version, stale data size, and optional compression workers.
- `NewTableBuilder` initializes allocator/block state and starts block worker goroutines when compression or encryption is enabled.
- `Add`, `AddStaleKey`, `addInternal`, and `addHelper` append entries and split blocks.
- `finishBlock` writes entry offsets and checksum and queues background compression/encryption.
- `ReachedCapacity` estimates whether the table is near configured capacity.
- `Finish` and `Done` finalize all blocks, build the index, and compute final table size.
- `encrypt`, `compressData`, `buildIndex`, and block-offset writers implement format details.

## Control Flow and State Behavior
Each block starts with a base key. Subsequent entries store a 4-byte `header` with overlap and diff length, followed by the key suffix and encoded `ValueStruct`. Entry offsets are collected for binary search. When `shouldFinishBlock` estimates the next entry would exceed `BlockSize`, the current block is finalized and a fresh block is allocated.

If compression or encryption is active, finalized blocks are sent to worker goroutines. `Done` closes the channel, waits for workers, builds an optional bloom filter from parsed user-key hashes, writes FlatBuffer `TableIndex` metadata, optionally encrypts the index, and appends index/checksum length footers. `buildData.Copy` lays blocks, index, index length, checksum, and checksum length into the final byte sequence.

## Dependencies and Integration Points
The builder is consumed by table creation, normal flush/compaction paths, and `StreamWriter.sortedWriter`. It depends on Badger flatbuffers (`fb`), protobuf checksums (`pb`), compression libraries (`s2`, ZSTD helpers), encryption helpers, options, and `z.AllocatorPool`.

## Risks and Edge Cases
The builder assumes keys are added in sorted order by callers; it does not enforce ordering itself. Size estimates are intentionally rough and include comments noting discrepancies. Compression/encryption workers must be drained by `Done`; `Close` should return the allocator after finish. Unsafe header encode/decode must match iterator expectations. Encryption appends IVs, so readers must use matching `DataKey`.

## Test Signals
`builder_test.go` validates block indexes under no compression, encryption, compression, and both; invalid decompression errors; bloom filter behavior; empty builders; and performance benchmarks for compression/encryption modes.
