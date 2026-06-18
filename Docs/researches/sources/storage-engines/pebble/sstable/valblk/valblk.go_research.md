# sources/storage-engines/pebble/sstable/valblk/valblk.go

## Purpose
Documents and implements value-block handle and index encodings for Pebble v3+ SSTables, where older MVCC values may be separated from data blocks for read locality.

## Important APIs, Types, And Functions
`Handle` stores value length, value block number, and offset. `HandleMaxLen`, `EncodeHandle`, `DecodeLenFromHandle`, `DecodeRemainingHandle`, and `DecodeHandle` encode/decode variable-width handles. `IndexHandle` stores the block handle plus fixed field widths. `EncodeIndexHandle`, `DecodeIndexHandle`, `DecodeIndex`, `DecodeBlockHandleFromIndex`, `littleEndianPut`, `lenLittleEndian`, and `littleEndianGet` implement index metadata.

## Control Flow
Data block values store a prefix plus varint handle. Readers can decode length first for lazy-value attributes, then decode remaining block/offset only when fetching. The value index block stores fixed-width rows `(blockNum, blockOffset, blockLength)`, enabling direct lookup by `blockNum * rowWidth`.

## State And Persistence Behavior
Handle bytes persist inside data blocks. Index handles persist in the metaindex. Value index blocks persist in the SSTable and map logical value block numbers to physical block handles.

## Dependencies And Integration Points
Used by value-block writer/reader, block handle encoding, SSTable writer format v3+, and default internal value construction. Depends on Pebble `block` and `base` corruption errors.

## Risks And Edge Cases
Manual unsafe varint decoding assumes valid enough input length. Index decoding validates row length and sequential block numbers. Fixed-width field lengths must fit maximum offsets/lengths selected by the writer.

## Test Signals
Unit tests cover handle encode/decode, index-handle encode/decode, and little-endian helper round trips.
