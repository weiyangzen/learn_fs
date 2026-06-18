<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/key_value_block_test.go -->
# sources/storage-engines/pebble/sstable/colblk/key_value_block_test.go

## Purpose
`key_value_block_test.go` validates the simple key/value block format for metaindex and properties use cases through datadriven golden output.

## Important APIs, Types, And Functions
`TestMetaIndexBlock` builds a `KeyValueBlockWriter` where values are varint-encoded `block.Handle`s. `TestPropertiesBlock` builds a writer from literal key/value fields. Both initialize `KeyValueBlockDecoder` and print `DebugString`.

## Control Flow
Each datadriven test supports a `build` command. The metaindex test parses key, offset, and length, encodes the handle into a local fixed array, and adds the encoded bytes as the value. The properties test parses a key and value and adds them directly. Both finish all rows, initialize a decoder, and return the formatted block.

## State And Persistence Behavior
The tests persist the columnar block into an in-memory byte slice. Metaindex values exercise compact block-handle serialization as raw bytes; properties values exercise arbitrary raw value slices.

## Dependencies And Integration Points
The tests use `datadriven`, `crstrings`, `sstable/block.Handle`, and `testify/require`. They model the metaindex/properties block consumers that expect sorted key/value records.

## Risks
The tests validate layout and formatting, not the `All` iterator method. Inputs are simple whitespace-delimited fields, so values containing spaces are not covered.

## Test Signals
Golden debug strings guard the two-column layout, raw-byte offsets, and compatibility with encoded block-handle payloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/key_value_block_test.go -->
