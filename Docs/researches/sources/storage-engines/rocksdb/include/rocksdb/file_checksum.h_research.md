# sources/storage-engines/rocksdb/include/rocksdb/file_checksum.h

## Purpose

`file_checksum.h` defines RocksDB's public interfaces for whole-file checksum generation and manifest/ingestion checksum list handling. It lets table writers compute a checksum while writing and lets metadata APIs carry checksum values and function names for SST files.

## Important APIs, types, and functions

Constants define metadata states: `kUnknownFileChecksum` is the empty checksum, `kUnknownFileChecksumFuncName` means no factory was configured when written, `kNoFileChecksumFuncName` means no checksum metadata is available, and `kStandardDbFileChecksumFuncName` names the built-in CRC32C generator. `FileChecksumGenContext` passes `file_name` and requested checksum function name to factories.

`FileChecksumGenerator` has the lifecycle `Update` zero or more times, `Finalize` once, then `GetChecksum` and `Name`. `FileChecksumGenFactory : public Customizable` supports registry creation via `CreateFromString` and creates generators per file through `CreateFileChecksumGenerator`. `FileChecksumList` stores per-file checksum records with `reset`, `size`, `GetAllFileChecksums`, `SearchOneFileChecksum`, `InsertOneFileChecksum`, and `RemoveOneFileChecksum`. `NewFileChecksumList` and `GetFileChecksumGenCrc32cFactory` expose built-ins.

## Control flow and behavior

During table file writing, RocksDB or an external table builder creates a generator from the configured factory and updates it as bytes are written. After finalization, the checksum and function name can be stored in table properties or manifest metadata. Consumers use `FileChecksumList` to collect all checksums from a manifest or prepare checksum metadata for ingestion.

## State and persistence

The generator owns transient checksum accumulation state until finalized. Persistent checksum state is the checksum byte string and function name associated with a file number. Checksums may contain arbitrary non-printable bytes and should not be assumed to be human-readable. The built-in CRC32C factory uses big-endian encoding and is documented as compatible with many CRC32C implementations but unlike RocksDB's masked little-endian CRC32C usage elsewhere.

## Dependencies and integration points

The header depends on `Customizable` and `Status`. It integrates with file options metadata, external table builders, manifest checksum extraction in `experimental.h`, SST ingestion, and DB file checksum verification. Factories participate in the RocksDB configurable object registry.

## Risks and test signals

Lifecycle misuse is a risk: `GetChecksum` is only valid after `Finalize`, and factories should return `nullptr` for unrecognized requested names. Empty checksum strings are reserved for unknown state, so real generators should not return empty. Tests should cover generator lifecycle, CRC32C compatibility and byte order, unknown/unavailable metadata propagation, list insert/search/remove/reset behavior, duplicate file numbers, arbitrary binary checksum strings, and `CreateFromString` registry loading.
