# sources/storage-engines/tikv/components/engine_traits/src/sst.rs

Purpose: Defines generic external SST reader/writer support and file metadata.

Important APIs and control flow: `SstExt` associates reader, writer, and builder types. `SstReader` opens files with optional encryption manager, verifies checksums, and reports KV count/size. `SstWriter` puts ordered keys, writes deletion keys, reports file size, finishes to metadata, or finishes and returns a readable buffer. `ExternalSstFileReader` can reset. `SstCompressionType` parses `lz4`, `snappy`, and `zstd`. `SstWriterBuilder` configures DB/CF, in-memory mode, compression type/level, and builds writers. `ExternalSstFileInfo` exposes path, key bounds, sequence number, file size, and entry count.

State, persistence, and dependencies: Writers create persistent or in-memory SST artifacts; readers inspect them. Dependencies include encryption `DataKeyManager` and import SST metadata.

Integration points, risks, and test signals: Used by import, snapshot, backup/restore, and range-delete-by-writer. Risks include ordered-key enforcement, delete-only files, compression compatibility, encryption metadata, checksum failures, and sequence-number semantics. Shared SST tests cover empty files, forward/reverse iteration, deletes, duplicate/reverse keys, file path, bounds, entry count, and file size.
