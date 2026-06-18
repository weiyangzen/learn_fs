# sources/storage-engines/pebble/sstable/blob/blocks.go

## Purpose
This file implements the columnar encoders and decoders for blob file index blocks and blob value blocks.

## Important APIs, Types, and Functions
`indexBlockEncoder` tracks physical block count, virtual block count, virtual block mappings, offsets, and a colblk encoder. `AddBlockHandle` records block start/end offsets. `AddVirtualBlockMapping` maps original virtual block IDs to physical block indexes and value-ID offsets, filling gaps as unreferenced. `Finish` serializes the index block with a custom header containing virtual block count.

`indexBlockDecoder` decodes virtual block mappings and offsets. `BlockHandle`, `RemapVirtualBlockID`, `BlockCount`, `DebugString`, and `Describe` expose decoded metadata.

`initIndexBlockMetadata` casts block metadata to an index decoder and converts initialization panics into corruption errors.

`blobValueBlockEncoder` stores blob values in a single `colblk.RawBytesBuilder` column. `Init`, `Reset`, `AddValue`, `Count`, `size`, and `Finish` manage encoding and serialization.

`blobValueBlockDecoder` decodes the raw-bytes column and provides `DebugString` and `Describe` diagnostics. `initBlobValueBlockMetadata` initializes decoder metadata and converts panics into corruption errors.

## Control Flow
Index encoding stores offsets as `n+1` entries for `n` physical blocks. The first handle records offset 0, later handles must start at the previous end offset or panic. Virtual mappings must be added in ascending virtual ID order; gaps are filled with sentinel mappings to unreferenced blocks. Decoding reads the virtual count from the first four bytes, then decodes virtual and offset columns from the colblk block. Value-block encoding serializes all pending raw values into one colblk block and appends the standard padding byte.

## State and Persistence Behavior
The index block is persisted inside each blob file and drives all later value retrieval. Physical block lengths are inferred from adjacent offsets minus `block.TrailerLen`. Virtual mappings preserve handle compatibility after blob file rewrite. Each physical value block persists a count of rows and raw-byte offsets/data for constant-time value lookup.

## Dependencies and Integration Points
The implementation depends on `colblk` builders/decoders, `block.Handle`, block metadata casting, `binfmt` and `treeprinter` diagnostics, invariants bounds checks, and base corruption/assertion errors. It is consumed by `FileWriter`, `FileReader`, `ValueFetcher`, and `FileRewriter`.

## Risks
Incorrect offset accounting corrupts all blob value reads. The virtual-block sentinel uses the low 32 bits as `0xffffffff`; readers treat a value-ID offset equal to that mask as unreferenced, so encoding/decoding assumptions must remain aligned. Panic-to-corruption conversion is important for untrusted file data.

## Test Signals
`blocks_test.go` covers index block build, debug formatting, block handle lookup, and virtual block remapping. Fetcher and rewrite tests indirectly cover value block decoding.
