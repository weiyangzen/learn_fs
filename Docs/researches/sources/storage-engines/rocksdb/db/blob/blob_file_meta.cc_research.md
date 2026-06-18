# sources/storage-engines/rocksdb/db/blob/blob_file_meta.cc

## Purpose
Implements derived size calculation and debug formatting for blob file metadata objects.

## Important APIs and Control Flow
`SharedBlobFileMetaData::GetBlobFileSize` returns `BlobLogHeader::kSize + total_blob_bytes_ + BlobLogFooter::kSize`. `SharedBlobFileMetaData::DebugString` and stream output render file number, total count/bytes, checksum method, and checksum value as hex. `BlobFileMetaData::DebugString` and stream output render the shared metadata, linked SST file numbers, garbage blob count, and garbage blob bytes.

## State, Dependencies, and Risks
This file does not mutate metadata; it exposes derived and diagnostic views. It depends on blob log format sizes and `Slice` hex rendering. Risks include derived file size assuming fixed header/footer and `total_blob_bytes_` already including record headers/key/value bytes as maintained elsewhere. Integration points include version/debug logging and metadata inspection.
