# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compression_manager.h

- **Purpose:** Defines a custom `CompressionManager` used by db_stress to exercise custom compression/decompression paths and compatibility-name persistence.
- **Important APIs/types/functions:** Defines `DbStressCustomCompressionManager` with `Name`, `CompatibilityName`, `SupportsCompressionType`, `GetCompressor`, `GetDecompressor`, `GetDecompressorForTypes`, and static `Register`.
- **Control flow:** Supports built-in compression plus custom AA/AB/AC types. `GetCompressor` randomly chooses among the requested type and custom test algorithms; decompressor instances can restrict allowed types.
- **State and persistence behavior:** Holds a shared built-in default compression manager. Compression choices affect SST block contents and stored compression metadata.
- **Dependencies and integration points:** Uses test utility custom compressor/decompressor implementations and built-in v2 compression manager. Registration is implemented in the `.cc` file.
- **Risks:** Random compressor selection increases coverage but can complicate reproducibility if seed/thread-local random state changes. Compatibility name must remain stable for old SST readability.
- **Test signals:** Stress runs with custom compression should verify writes, reads, compactions, and reopen across files compressed with multiple custom algorithms.
