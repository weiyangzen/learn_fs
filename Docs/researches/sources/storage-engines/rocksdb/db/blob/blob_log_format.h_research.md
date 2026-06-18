<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_format.h -->
# sources/storage-engines/rocksdb/db/blob/blob_log_format.h

## Purpose
Declares the stable blob log file format: file header, file footer, record header, magic/version constants, expiration range representation, and offset validation helper.

## Important APIs, Types, and Functions
`BlobLogHeader` is a 30-byte header with version, column family, compression, TTL flag, and coarse expiration range. `BlobLogFooter` is a 32-byte footer with blob count, exact expiration range, and CRC. `BlobLogRecord` has a 32-byte fixed header plus key and value payloads. `BlobLogRecord::CalculateAdjustmentForRecordHeader` converts a BlobIndex value offset back to the record-header start. `IsValidBlobOffset` checks whether a value offset and size fit inside a blob file, optionally reserving footer bytes.

## Control Flow
Readers and writers use the declared sizes to read/write exact fixed sections. Blob indexes point to the value payload, so checksum-verifying readers subtract the key-size-plus-header adjustment before reading full records. Offset validation checks minimum prefix, key-size relationship, footer reservation, and value end bounds.

## State and Persistence Behavior
This header is the authoritative on-disk contract. Header/footer presence distinguishes fully sealed files from in-flight direct-write files, and `has_footer` in `IsValidBlobOffset` controls which tail bytes are considered available.

## Dependencies and Integration Points
It depends on RocksDB options, slices, status, and compression/type definitions. It is included by writer, sequential reader, file reader, garbage meter, partition manager, and tests.

## Risks and Edge Cases
`IsValidBlobOffset` is central to preventing underflow/overflow on corrupt indexes; changes must preserve unsigned arithmetic safety. Footerless validation is only safe for files known to be open direct-write files. The fixed-width layout favors simple random access but leaves no variable extension fields beyond versioning.

## Test Signals
Reader and writer tests indirectly validate header/footer/record sizes, CRC behavior, offset adjustment, TTL rejection, malformed file detection, and footerless direct-write interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_log_format.h -->
