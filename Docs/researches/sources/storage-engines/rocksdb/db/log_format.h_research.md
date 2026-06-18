# sources/storage-engines/rocksdb/db/log_format.h

## Purpose

`log_format.h` defines the shared WAL/log record format constants used by RocksDB log readers and writers. It contains the record type enum, safe-ignore mask, maximum record type, block size, and header sizes for normal and recyclable log records.

The file is a compact wire-format contract. Changes here affect compatibility between WAL writers, WAL readers, recovery, recyclable log handling, compression records, user-defined timestamp size records, and WAL verification metadata.

## Important APIs, types, and functions

- `log::RecordType` is an 8-bit enum.
- `kZeroType` marks preallocated file space.
- `kFullType`, `kFirstType`, `kMiddleType`, and `kLastType` represent normal complete or fragmented records.
- `kRecyclableFullType`, `kRecyclableFirstType`, `kRecyclableMiddleType`, and `kRecyclableLastType` are recyclable log variants that carry a log number in the larger header.
- `kSetCompressionType` identifies compression type changes.
- `kUserDefinedTimestampSizeType` and `kRecyclableUserDefinedTimestampSizeType` store timestamp-size metadata; comments note that for values at or above 10, bit 0 indicates whether the record is recyclable.
- `kPredecessorWALInfoType` and `kRecyclePredecessorWALInfoType` support WAL verification.
- `kRecordTypeSafeIgnoreMask` is bit 7; unknown record types with this bit set may be ignored safely.
- `kMaxRecordType` is currently `kRecyclePredecessorWALInfoType`.
- `kBlockSize` is 32768 bytes.
- `kHeaderSize` is 7 bytes: checksum, length, and type.
- `kRecyclableHeaderSize` is 11 bytes: normal header plus 4-byte log number.

## Control flow

Log writers choose a `RecordType` based on whether a logical record fits in one block, needs fragmentation, belongs to a recyclable WAL, changes compression/timestamp metadata, or records WAL verification information. Log readers interpret the type byte using this enum and the corresponding header size. Fragmented records are reconstructed from first/middle/last sequences; full records stand alone.

The safe-ignore mask gives readers a way to skip newer unknown record types when bit 7 is set. `kMaxRecordType` bounds the currently known type range for validation.

## State and persistence behavior

All constants here define persistent WAL bytes. Normal records store a 4-byte checksum, 2-byte length, and 1-byte type. Recyclable records add a 4-byte log number. `kBlockSize` fixes the fragmentation and padding unit. `kZeroType` allows preallocated zeroed regions.

Because these constants are persistent-format contracts, changing numeric enum values, block size, or header sizes can break recovery compatibility with existing WAL files.

## Dependencies and integration points

The file only depends on `<cstdint>` and `rocksdb/rocksdb_namespace.h`. It is included by log reader and writer implementations, DB recovery, WAL recycling code, compression/timestamp metadata handling, and WAL verification code.

It also points maintainers to `../doc/log_format.txt` for detailed format documentation.

## Risks and edge cases

- Numeric enum values are compatibility-sensitive and should not be reordered.
- Unknown types without `kRecordTypeSafeIgnoreMask` should be treated as errors by readers; new ignorable extensions need the high bit set.
- Recyclable and non-recyclable record pairs must stay aligned with header parsing logic.
- Fragmentation correctness depends on `kBlockSize` and `kHeaderSize`; changing either affects every reader/writer boundary calculation.
- Values `>= 10` use bit 0 as recyclable indication by convention, so future type allocation must preserve that scheme where applicable.

## Test signals

Relevant tests include WAL writer/reader round trips for full and fragmented records, recyclable WAL recovery, preallocated zero handling, compression and user-defined timestamp records, safe-ignore behavior for unknown high-bit types, corrupted header detection, and predecessor WAL info verification. Recovery tests should include old WALs to guard format compatibility.
