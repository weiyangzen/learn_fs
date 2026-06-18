<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_reader.h -->
# sources/storage-engines/rocksdb/db/log_reader.h

## Purpose
Declares the general-purpose log stream reader interfaces used to read RocksDB log-format files. The header exposes `log::Reader` for standard blocking scans and `log::FragmentBufferedReader` for tailing/retry scenarios where a physical record may be partially available.

## Important APIs, Types, And Functions
`Reader::Reporter` is the callback interface for corruption and old-log notifications. `Reader` owns a `SequentialFileReader`, an optional reporter, checksum and WAL-verification settings, block buffer storage, compression state, timestamp-size state, and offset accounting. Public APIs include `ReadRecord()`, `GetRecordedTimestampSize()`, `LastRecordOffset()`, `LastRecordEnd()`, `IsEOF()`, `hasReadError()`, `UnmarkEOF()`, `file()`, `GetReporter()`, `GetLogNumber()`, `GetReadOffset()`, and `IsCompressedAndEmptyFile()`.

Protected helpers define the physical-record layer: `ReadPhysicalRecord()`, `ReadMore()`, `UnmarkEOFInternal()`, `ReportCorruption()`, `ReportDrop()`, `ReportOldLogRecord()`, `InitCompression()`, `UpdateRecordedTimestampSize()`, and `MaybeVerifyPredecessorWALInfo()`. The private-like enum extends record types with internal sentinel values such as `kEof`, `kBadRecord`, `kBadHeader`, `kOldRecord`, `kBadRecordLen`, and `kBadRecordChecksum`. `FragmentBufferedReader` overrides `ReadRecord()` and `UnmarkEOF()` and adds retained `fragments_` state plus `TryReadFragment()`/`TryReadMore()`.

## Control Flow
The header establishes the split between logical records and physical records. Callers repeatedly call `ReadRecord()` and receive complete logical payloads while the implementation hides block fragmentation, side records, decompression, and recovery-mode decisions. EOF can be cleared with `UnmarkEOF()` when the caller knows a file has grown. The fragment-buffered subclass keeps partially assembled logical fragments across calls so a later call can finish a record after a writer appends the missing bytes.

## State And Persistence Behavior
`Reader` is non-copyable and requires the underlying file and reporter to remain valid for its lifetime. Its state is in-memory only, but it directly controls persistent recovery semantics by deciding which bytes from a WAL are replayed, dropped, reported, or treated as stale. `recorded_cf_to_ts_sz_` accumulates side-record metadata applying to subsequent WAL records. Compression state is initialized lazily from a leading compression-type record.

## Dependencies And Integration Points
Includes `db/log_format.h`, `file/sequence_file_reader.h`, RocksDB options/status/slice types, compression utilities, hash containers, UDT utilities, and XXH3. It is consumed by WAL recovery, log tests, and any component reading RocksDB's log format. It must remain format-compatible with `log_writer.h`/`log_writer.cc`.

## Risks And Edge Cases
The contract around scratch lifetimes is important: returned slices are valid only until reader mutation or scratch mutation. Reporter lifetime is external. Subclassing is limited but real; changes to protected state or sentinel values can break `FragmentBufferedReader`. WAL verification fields are reader-level state, while recovery mode is per-call, so callers must pass consistent recovery mode when replaying a file.

## Test Signals
The public API is exercised heavily in `log_test.cc`, especially through both `Reader` and `FragmentBufferedReader` parameterizations. Tests validate `IsEOF()`, `UnmarkEOF()`, timestamp-size maps, recyclable-log behavior, and checksum calculation expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/log_reader.h -->
