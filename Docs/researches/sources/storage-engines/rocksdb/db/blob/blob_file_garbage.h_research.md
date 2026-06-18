# sources/storage-engines/rocksdb/db/blob/blob_file_garbage.h

## Purpose
Declares `BlobFileGarbage`, the manifest record that accumulates garbage blob count and bytes for a blob file.

## Important APIs and State
The class stores blob file number, garbage blob count, and garbage blob bytes. Defaults use `kInvalidBlobFileNumber` and zero counts. Accessors expose fields. `EncodeTo`, `DecodeFrom`, `DebugString`, and `DebugJSON` provide persistence and diagnostics. Equality, inequality, stream, and JSON operators are declared.

## Dependencies, Risks, and Integration
It depends on blob constants, `Slice`, `Status`, and `JSONWriter`. It integrates with version edit/application logic that tracks blob garbage from compactions. Risks include persisted-format compatibility and callers constructing garbage counts beyond total file counts; that cross-check is likely enforced by higher-level metadata/version code. Tests in `blob_file_garbage_test.cc` validate the record-level contract.
