# sources/storage-engines/badger/fb/TableIndex.go

## Purpose
`fb/TableIndex.go` is generated FlatBuffers code for Badger table index metadata. It exposes block offsets, bloom filter bytes, max version, key count, size metrics, and stale-data size.

## Important APIs, Types, and Functions
- `TableIndex`: wrapper around `flatbuffers.Table`.
- `GetRootAsTableIndex`, `Init`, `Table`: buffer initialization.
- Accessors/mutators: `Offsets`, `OffsetsLength`, `BloomFilter`, `BloomFilterLength`, `BloomFilterBytes`, `MutateBloomFilter`, `MaxVersion`, `KeyCount`, `UncompressedSize`, `OnDiskSize`, `StaleDataSize`, and their mutators.
- Builder helpers: `TableIndexStart`, `TableIndexAddOffsets`, `TableIndexStartOffsetsVector`, `TableIndexAddBloomFilter`, `TableIndexStartBloomFilterVector`, `TableIndexAddMaxVersion`, `TableIndexAddKeyCount`, `TableIndexAddUncompressedSize`, `TableIndexAddOnDiskSize`, `TableIndexAddStaleDataSize`, `TableIndexEnd`.

## Control Flow and State
The code is a thin generated layer over FlatBuffers. Accessors check whether a field offset exists and otherwise return zero/empty defaults. `Offsets` initializes a supplied `BlockOffset` from an indirect vector element.

## Persistence Behavior
This schema-backed metadata is part of SST table persistence. `MaxVersion` supports iterator and compaction filtering; bloom filter and offset data support efficient reads; size/stale metrics support compaction and GC decisions.

## Dependencies and Integration Points
Depends on `flatbuffers/go` and `BlockOffset`. Integrated with table builder/reader code and indirectly with iterator, level handler, checksum, and loading tests.

## Risks and Edge Cases
As generated persistence code, schema drift is the major risk. Absence defaults can mask malformed or older table index buffers unless higher layers validate required fields.

## Test Signals
Indirectly covered by table creation, DB load, iterator prefix picking, checksum verification, and compaction tests.
