<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/options/options.go -->
# sources/storage-engines/badger/options/options.go

## Purpose
This file defines small public enum types used to configure SSTable checksum verification and block compression.

## Important APIs, Types, And Functions
`ChecksumVerificationMode` supports `NoVerification`, `OnTableRead`, `OnBlockRead`, and `OnTableAndBlockRead`. `CompressionType` supports `None`, `Snappy`, and `ZSTD`.

## Control Flow
There is no runtime control flow in this file; consumers compare enum values and pass them into DB/table options.

## State And Persistence Behavior
Compression type is persisted indirectly for SSTables through manifest/table metadata and determines how table blocks are encoded. Checksum verification mode affects read/open validation behavior but is not itself persisted.

## Dependencies And Integration Points
The package is imported by `badger/options.go`, `manifest.go`, table builders/openers, tests, and any external callers configuring Badger.

## Risks And Edge Cases
Enum numeric values are part of the public API and compression values are persisted in manifest changes, so changing them would break compatibility. Adding values requires updates to parsing, docs, tests, and table handling.

## Test Signals
`options_test.go` exercises compression enum parsing through superflags. Manifest and table-opening paths indirectly rely on these values.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/options/options.go -->
