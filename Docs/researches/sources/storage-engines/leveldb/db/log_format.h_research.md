# sources/storage-engines/leveldb/db/log_format.h

## Purpose
This header defines the physical write-ahead log record format shared by log reader and writer.

## Important APIs, Types, And Functions
`log::RecordType` defines `kZeroType`, `kFullType`, `kFirstType`, `kMiddleType`, and `kLastType`, with `kMaxRecordType = kLastType`. Constants `kBlockSize = 32768` and `kHeaderSize = 7` define block and header sizes.

## Control Flow
There is no executable code. The comments define that each header stores checksum (4 bytes), length (2 bytes), and type (1 byte), and that fragmented logical records use first/middle/last records.

## State And Persistence Behavior
This is a persistent WAL and descriptor-log format contract. Writers pad block trailers and readers use these constants to reassemble logical records and detect corruption.

## Dependencies And Integration Points
It is included by `log_reader`, `log_writer`, DB recovery, corruption tests, fault-injection tests, and log tests.

## Risks And Edge Cases
Changing constants or enum values would break existing logs and manifests. `kZeroType` is reserved for preallocated file regions and must be handled specially by readers.

## Test Signals
`log_test.cc` heavily exercises block boundaries, trailers, fragmentation, corruption, and initial offsets using these constants.
