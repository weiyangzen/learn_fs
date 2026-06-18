<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.h -->
# sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.h

## Purpose
Declares `BlobLogSequentialReader`, a cursor-based stream reader over blob log files backed by `RandomAccessFileReader`.

## Important APIs, Types, and Functions
`ReadLevel` selects whether `ReadRecord` returns only the header, header plus key, or header plus key plus blob value. Public methods include `ReadHeader`, `ReadRecord`, `ReadFooter`, `ResetNextByte`, and `GetNextByte`. Private `ReadSlice` performs cursor-based file reads into caller-provided buffers.

## Control Flow
Callers read from byte zero through header, zero or more records, and footer. `ResetNextByte` allows repositioning to the beginning; otherwise reads are strictly sequential according to `next_byte_`.

## State and Persistence Behavior
State consists of the owned file reader, clock/statistics pointers, a temporary slice, fixed header buffer, and current byte offset. It is read-only with respect to persistent data.

## Dependencies and Integration Points
The header depends on blob log format and RocksDB slice types, and forward-declares file, env, statistics, status, and clock types. It complements `BlobLogWriter` and can be used by blob file scanning/recovery tools.

## Risks and Edge Cases
The `MAX_HEADER_SIZE` macro is local but non-idiomatic and must track all fixed header/footer sizes. The API assumes records are consumed in order and does not expose arbitrary seek except reset. Payload allocations occur in the implementation based on decoded sizes.

## Test Signals
Coverage should assert all read levels, cursor values, footer decode, short-read handling, and blob offset calculation. No dedicated test file appears in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_sequential_reader.h -->
