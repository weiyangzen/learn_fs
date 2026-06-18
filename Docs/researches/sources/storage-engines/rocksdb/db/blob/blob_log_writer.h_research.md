<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_writer.h -->
# sources/storage-engines/rocksdb/db/blob/blob_log_writer.h

## Purpose
Declares `BlobLogWriter`, the append-only writer abstraction for RocksDB blob log files.

## Important APIs, Types, and Functions
The constructor takes ownership of a `WritableFileWriter`, clock/statistics pointers, blob file number, fsync setting, flush policy, and optional starting offset. Public methods include `ConstructBlobHeader`, `AddRecord` overloads, `EmitPhysicalRecord`, `AppendFooter`, `WriteHeader`, `file`, `get_log_number`, and `Sync`. `last_elem_type_` tracks header/record/footer order for assertions.

## Control Flow
Callers create a writer for an empty file, write the header, add records, then append the footer. Record appends return both key offset and value offset; BlobIndex stores the value offset. Footer append closes the underlying file.

## State and Persistence Behavior
State includes the owned writable file, logical file number, current block/file offset, fsync and flush policies, and last element type. The writer is the persistence boundary for blob log bytes and file-level checksum metadata.

## Dependencies and Integration Points
The header depends on blob log format, slices, statistics, statuses, write options, and `WritableFileWriter`. It is used by blob DB write builders, direct-write partition manager, tests, and any code that creates blob files.

## Risks and Edge Cases
The API exposes `EmitPhysicalRecord`, so callers can bypass expiration-specific helpers if misused. Method-order correctness is assertion-based. The writer owns and may reset `dest_` on footer append, so external users must not retain stale raw file pointers after finalization.

## Test Signals
Round-trip tests through `BlobFileReader` validate writer output. Additional coverage should verify footer append after zero records, seen-error behavior, fsync/flush paths, and checksum output.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_writer.h -->
