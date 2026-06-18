<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_read_request.h -->
# sources/storage-engines/rocksdb/db/blob/blob_read_request.h

## Purpose
Defines the request structures shared by `BlobSource::MultiGetBlob` and `BlobFileReader::MultiGetBlob`.

## Important APIs, Types, and Functions
`BlobReadRequest` contains a user-key pointer, blob value offset, stored length, compression type, output `PinnableSlice`, and output `Status`. Its constructor binds these fields to caller-owned objects. `BlobFileReadRequests` groups a blob file number, file size, and an `autovector` of requests for that file.

## Control Flow
Higher-level code groups blob indexes by file, creates `BlobReadRequest` objects, sorts requests by offset before reader calls, and expects each request status/result to be filled independently. Cache hits can complete some requests while misses are passed to `BlobFileReader`.

## State and Persistence Behavior
This header defines transient stack/request state only. It does not own user keys, results, or statuses; those pointers must outlive the multiget call.

## Dependencies and Integration Points
It depends on compression enums, `Slice`, `Status`, `PinnableSlice`, and `autovector`. It is included by blob source and reader components and ties multiget request plumbing to caller-owned status/result storage.

## Risks and Edge Cases
Default construction leaves pointers null, so implementations assert fields before use. Copying is shallow; copied requests still point at the same user key, result, and status. `len` is a `size_t` while offsets and file sizes are `uint64_t`, so callers must avoid truncation when converting from blob metadata.

## Test Signals
Reader and source multiget tests validate status/result mutation, sorted-offset expectations, cache-hit/miss handling, and partial failure semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_read_request.h -->
