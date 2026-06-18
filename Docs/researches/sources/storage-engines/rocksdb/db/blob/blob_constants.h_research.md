# sources/storage-engines/rocksdb/db/blob/blob_constants.h

## Purpose
Defines blob subsystem constants shared by metadata and manifest record classes.

## Important APIs and State
The file declares `constexpr uint64_t kInvalidBlobFileNumber = 0` inside the RocksDB namespace. It is used as the default sentinel for classes such as `BlobFileAddition` and `BlobFileGarbage`.

## Dependencies, Risks, and Test Signals
There is no control flow or persistence. The dependency surface is intentionally tiny: `<cstdint>` and namespace declaration. The key invariant is that valid blob file numbers must not be zero. Tests in metadata/addition/garbage files assert default objects use this sentinel.
