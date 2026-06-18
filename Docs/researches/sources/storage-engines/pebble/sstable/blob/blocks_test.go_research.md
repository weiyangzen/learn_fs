# sources/storage-engines/pebble/sstable/blob/blocks_test.go

## Purpose
This file provides datadriven coverage for blob index block encoding and decoding.

## Important APIs, Types, and Functions
`TestIndexBlockEncoding` supports `build`, `get`, and `remap-virtual-blockid`. It builds an `indexBlockEncoder` from input block handles and optional virtual mappings, initializes an `indexBlockDecoder`, prints debug structure, retrieves physical block handles, and remaps virtual IDs.

## Control Flow
The `build` command reads offset/length lines until a `virtual-block-mappings` marker, then parses mapping rows as virtual block ID, physical block index, and value ID offset. Subsequent commands operate on the last decoded block.

## State and Persistence Behavior
The encoded index block is held in memory by the decoder across datadriven commands.

## Dependencies and Integration Points
The test uses `datadriven`, `crstrings`, `block.Handle`, and `require`. It directly tests index block APIs used by blob readers and rewriters.

## Risks
Debug-string golden output can change when colblk formatting changes. The test focuses on index blocks and does not cover value block payloads.

## Test Signals
Expected output validates offset-column encoding, custom header decoding, virtual mapping gap behavior, block handle reconstruction, and remap results.
