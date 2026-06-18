<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/sst_importer.rs -->
# sources/storage-engines/tikv/components/error_code/src/sst_importer.rs

Purpose: this module declares SST importer error codes under `KV:SstImporter:`, used by TiKV import/ingest paths.

Important APIs and constants: the namespace covers I/O and transport (`IO`, `GRPC`), identifiers and futures (`UUID`, `FUTURE`), RocksDB/engine failures (`ROCKSDB`, `ENGINE`), file validation (`FILE_EXISTS`, `FILE_CORRUPTED`, `INVALID_SST_PATH`, `INVALID_CHUNK`, `BAD_FORMAT`, `FILE_CONFLICT`), external storage (`CANNOT_READ_EXTERNAL_STORAGE`), API/TTL/key-mode compatibility, request staleness, disk space, mismatched requests, and `ERROR_WRAPPER`. `SUSPENDED` includes non-empty diagnostic metadata.

Control flow and state: this is declarative macro expansion with lazy `ALL_ERROR_CODES`. No conversion trait implementation is local to the file.

Dependencies and integration points: importer code maps domain errors to these constants, and `bin.rs` includes the namespace in generated catalog output.

Risks: `RESOURCE_NOT_ENOUTH` has a spelling error in the constant name while the suffix is `ResourceNotEnough`; changing the Rust constant would affect source compatibility. Most descriptions are empty. Some code suffix casing, such as `MisMatchedRequest`, may be externally stable despite inconsistency.

Test signals: no module-local tests exist. Compilation checks macro syntax only.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/sst_importer.rs -->
