# sources/storage-engines/leveldb/util/coding.cc

## Purpose
`coding.cc` implements endian-neutral fixed-width, varint, and length-prefixed slice encodings used throughout LevelDB's persistent formats.

## Important APIs, Types, and Functions
Functions include `PutFixed32`, `PutFixed64`, `EncodeVarint32`, `PutVarint32`, `EncodeVarint64`, `PutVarint64`, `PutLengthPrefixedSlice`, `VarintLength`, `GetVarint32PtrFallback`, `GetVarint32`, `GetVarint64Ptr`, `GetVarint64`, and `GetLengthPrefixedSlice`.

## Control Flow
Fixed writes append little-endian bytes. Varint32 has unrolled cases for up to five bytes; varint64 loops until the high bit clears. Decode functions advance a `Slice` only on success, returning `nullptr`/`false` for truncation or overflow.

## State, Persistence, and Integration
There is no mutable state. These encodings are used by table handles, footers, block entries, filter offsets, hashes, logs, and DB internal records.

## Risks and Test Signals
Bounds handling and unsigned byte interpretation are critical. Tests cover fixed encodings, little-endian output, varint lengths, overflow, truncation, and length-prefixed strings.
