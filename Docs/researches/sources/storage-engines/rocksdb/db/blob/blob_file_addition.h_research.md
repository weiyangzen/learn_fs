# sources/storage-engines/rocksdb/db/blob/blob_file_addition.h

## Purpose
Declares `BlobFileAddition`, the manifest record describing a newly generated blob file.

## Important APIs and State
The class stores blob file number, total blob count, total blob bytes, checksum method, and checksum value. The default file number is `kInvalidBlobFileNumber`. The value constructor asserts checksum method/value are both empty or both non-empty. Accessors expose all fields. `EncodeTo`, `DecodeFrom`, `DebugString`, and `DebugJSON` provide persistence and diagnostics. Equality, inequality, stream, and JSON operators are declared.

## Dependencies, Risks, and Integration
It depends on blob constants, `Slice`, `Status`, and `JSONWriter`. The object is used by `BlobFileBuilder` when a blob file closes successfully and by version/manifest logic that applies blob-file additions. Risks are persisted-format compatibility and callers treating default records as valid additions. Tests in `blob_file_addition_test.cc` cover the public contract.
