# sources/storage-engines/leveldb/util/crc32c.cc

## Purpose
`crc32c.cc` provides CRC32C computation for block/log checksum protection, with optional hardware acceleration.

## Important APIs, Types, and Functions
`crc32c::Extend` is the exported implementation. Internal state includes byte and stride extension lookup tables, `ReadUint32LE`, `RoundUp`, and `CanAccelerateCRC32C`.

## Control Flow
At first use, `CanAccelerateCRC32C` probes `port::AcceleratedCRC32C` against a known vector. If available, `Extend` delegates. Otherwise it preconditions the initial CRC, processes unaligned bytes, processes 16-byte chunks across four stride CRC streams, folds partial CRCs, processes trailing bytes, and postconditions the result.

## State, Persistence, and Integration
A function-local static caches acceleration availability. CRC values are persisted in table block trailers and other on-disk records through masked values from `crc32c.h`.

## Risks and Test Signals
Hardware probe correctness is essential because a bad accelerated implementation would corrupt verification globally. Portable code relies on little-endian decode helpers and table constants. Tests cover RFC vectors, extension equivalence, and mask/unmask behavior.
