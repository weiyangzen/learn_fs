# sources/storage-engines/leveldb/db/log_reader.cc

## Purpose
This file implements the LevelDB log reader that reconstructs logical records from physical WAL/manifest fragments, verifies checksums, handles corruption, and supports reading from an initial physical offset.

## Important APIs, Types, And Functions
`Reader::Reporter::~Reporter`, constructor/destructor, `SkipToInitialBlock`, `ReadRecord`, `LastRecordOffset`, `ReportCorruption`, `ReportDrop`, and `ReadPhysicalRecord` are implemented. Special internal record results are `kEof` and `kBadRecord`.

## Control Flow
`ReadRecord` skips to the first eligible block, then loops over physical records. Full records return immediately; first/middle/last fragments are appended into `scratch`; unexpected fragment types report corruption; EOF discards incomplete trailing logical records without corruption. Initial-offset resync silently skips middle/last fragments until a new full/first record. `ReadPhysicalRecord` refills 32 KiB blocks, parses headers, validates lengths, ignores zero-length preallocation records, checks CRC if enabled, and skips records beginning before the initial offset.

## State And Persistence Behavior
The reader is read-only but recovery-critical. It reports dropped bytes only when the dropped region is at or after the initial offset. It treats truncated final headers/records as EOF to tolerate writer crashes.

## Dependencies And Integration Points
It depends on `SequentialFile`, `Slice`, `Status`, log format constants, fixed coding, and crc32c. DB recovery and dump utilities use it for WAL and manifest records.

## Risks And Edge Cases
Checksum mismatch drops the rest of the buffer because length may be corrupt. Initial offset handling must avoid returning partial logical records. The "earlier writer empty first record" compatibility path suppresses false corruption for old logs.

## Test Signals
`log_test.cc` covers normal reads, fragmentation, trailers, append reopen, read errors, bad type/length/checksum, missing fragments, joining-prevention after corrupted blocks, and initial-offset positioning.
