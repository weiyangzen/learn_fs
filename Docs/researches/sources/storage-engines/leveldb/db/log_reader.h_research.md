# sources/storage-engines/leveldb/db/log_reader.h

## Purpose
This header declares the WAL/manifest log `Reader` and its corruption reporting interface.

## Important APIs, Types, And Functions
`Reader::Reporter` exposes virtual `Corruption(size_t bytes, const Status& status)`. `Reader` exposes constructor, destructor, `ReadRecord(Slice* record, std::string* scratch)`, and `LastRecordOffset`. Private declarations cover initial block skipping, physical record reading, and corruption/drop reporting.

## Control Flow
The public contract states that returned record data is valid only until the next mutating reader operation or scratch mutation. The constructor accepts `checksum` and `initial_offset`, enabling recovery/dump modes and offset-based readers.

## State And Persistence Behavior
Members track file pointer, reporter, checksum flag, backing block buffer, EOF, last record offset, end-of-buffer offset, initial offset, and resync mode. These fields drive safe recovery from partial or corrupted persistent logs.

## Dependencies And Integration Points
It depends on log format constants, public `Slice`/`Status`, and forward-declared `SequentialFile`. It is used by `db_impl.cc`, `dumpfile.cc`, and log tests.

## Risks And Edge Cases
The file passed to `Reader` and reporter must outlive the reader. Incorrect scratch lifetime handling by callers can invalidate returned records. Initial-offset semantics are physical-offset based, not logical sequence based.

## Test Signals
Coverage is direct through `log_test.cc`, especially corruption reporting and offset tests.
