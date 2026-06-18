# sources/storage-engines/rocksdb/db/blob/blob_file_meta.h

## Purpose
Declares shared and version-specific blob file metadata models used by RocksDB versions.

## Important APIs and State
`SharedBlobFileMetaData` is immutable, non-copyable/non-movable, and intended to be shared across versions for the same blob file. Static `Create` overloads construct shared pointers, optionally with a custom deleter used to mark obsolescence on destruction. It stores file number, total blob count/bytes, checksum method, and checksum value. `BlobFileMetaData` wraps shared metadata with version-specific `linked_ssts_`, garbage blob count, and garbage blob bytes. It asserts garbage does not exceed total counts/bytes and forwards shared accessors.

## Dependencies, Risks, and Integration
The metadata is in-memory version state derived from manifest additions/garbage records and blob file lifecycle. Dependencies are C++ shared ownership and unordered sets. Risks include non-deterministic linked-SST debug ordering, custom deleter side effects, and invariant checks being assertions rather than runtime status. Integration points are VersionSet/version edits, blob garbage collection, obsolete-file deletion, and debug logging.
