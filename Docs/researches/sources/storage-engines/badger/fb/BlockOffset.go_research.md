# sources/storage-engines/badger/fb/BlockOffset.go

## Purpose
`fb/BlockOffset.go` is generated FlatBuffers Go code for table block-offset metadata. It gives Badger's table code zero-copy accessors/builders for a block key, offset, and length.

## Important APIs, Types, and Functions
- `BlockOffset`: wrapper around `flatbuffers.Table`.
- `GetRootAsBlockOffset`, `Init`, `Table`: initialize access to serialized buffers.
- Accessors/mutators: `Key`, `KeyLength`, `KeyBytes`, `MutateKey`, `Offset`, `MutateOffset`, `Len`, `MutateLen`.
- Builder helpers: `BlockOffsetStart`, `BlockOffsetAddKey`, `BlockOffsetStartKeyVector`, `BlockOffsetAddOffset`, `BlockOffsetAddLen`, `BlockOffsetEnd`.

## Control Flow and State
Accessors compute vtable offsets and return default zero values when fields are absent. Mutators delegate to FlatBuffers slot/vector mutation helpers. Builder functions must be called in FlatBuffers reverse-construction order by table-building code.

## Persistence Behavior
This code defines the binary layout API for serialized SST table index data. The source is generated and should match `flatbuffer.fbs`; manual edits risk on-disk incompatibility.

## Dependencies and Integration Points
Depends on `github.com/google/flatbuffers/go`. Used by Badger table index encoding/decoding code outside this subset.

## Risks and Edge Cases
Generated code lacks semantic validation of vector bounds or schema compatibility beyond FlatBuffers mechanics. Regeneration with a different flatc version or schema can affect binary compatibility.

## Test Signals
No direct tests in this subset. Table read/write, iterator, checksum, and load tests indirectly exercise serialized table metadata.
