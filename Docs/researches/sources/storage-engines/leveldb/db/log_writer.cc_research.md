# sources/storage-engines/leveldb/db/log_writer.cc

## Purpose
This file implements the physical log writer for WAL and descriptor records.

## Important APIs, Types, And Functions
`InitTypeCrc`, `Writer` constructors, destructor, `AddRecord`, and `EmitPhysicalRecord` are implemented. `type_crc_` caches CRC seeds for record-type bytes.

## Control Flow
`AddRecord` fragments a logical slice across 32 KiB blocks. If fewer than seven bytes remain in a block, it pads the trailer with zeros and starts a new block. It emits at least one physical record even for empty slices, choosing full/first/middle/last type from begin/end state. `EmitPhysicalRecord` writes a seven-byte header with masked crc32c over type+payload, little-endian length, type, then appends payload and flushes.

## State And Persistence Behavior
The writer appends to a `WritableFile` and tracks `block_offset_`. The second constructor resumes append mode from an existing file length. It flushes after every physical record but leaves durable syncing to callers such as `DBImpl::Write`.

## Dependencies And Integration Points
It depends on `WritableFile`, log format constants, fixed coding, and crc32c. It is used for DB WAL records, manifest/descriptor records, DB creation, and tests.

## Risks And Edge Cases
Record length must fit in 16 bits, guaranteed by block fragmentation. Padding relies on `kHeaderSize == 7`. Flush without sync means callers must handle durability explicitly. Append-mode offset must match actual file length.

## Test Signals
`log_test.cc` validates empty records, many records, fragmentation, marginal trailers, append reopen, random reads, and reader corruption behavior against writer output.
