# sources/storage-engines/leveldb/table/format.cc

## Purpose
`format.cc` implements encoding/decoding of table block handles and footers plus block reads, decompression, and checksum validation.

## Important APIs, Types, and Functions
`BlockHandle::EncodeTo`, `DecodeFrom`, `Footer::EncodeTo`, `DecodeFrom`, and `ReadBlock` are the core functions. It uses `kTableMagicNumber`, `kBlockTrailerSize`, compression types, and `BlockContents`.

## Control Flow
Block handles encode offset and size as varints. Footers encode metaindex and index block handles, pad to a fixed length, and append the magic number. `ReadBlock` reads `handle.size + trailer`, optionally checks masked CRC32C over contents plus compression type, then either returns the raw bytes or decompresses Snappy/Zstd into heap memory.

## State, Persistence, and Integration
This file defines persistent SSTable wire format details consumed by `Table::Open` and produced by `TableBuilder`. `BlockContents::heap_allocated` and `cachable` steer block ownership and cache insertion.

## Risks and Test Signals
Incorrect handle decoding, footer padding, trailer size, checksum masks, or compression fallback breaks table compatibility. Table tests verify plain/compressed offset behavior and round-trip table reads.
