# sources/storage-engines/rocksdb/table/table_builder.h

Purpose: declares the generic table-building options and abstract `TableBuilder` interface used by all RocksDB table formats.

Important APIs/types/functions: `TableReaderOptions` bundles immutable options, prefix extractor, compression manager, env options, comparator, filter skipping, immortality, prefetch flags, level, tracing, cache pinning, DB/session/file identity, unique ID, protection bytes, tail size, timestamp persistence, and metadata-cache policy. `TableBuilderOptions` extends table-property collector context with immutable/mutable/read/write options, comparator, collector factories, compression settings, column-family identity, level, key-time metadata, bottommost/reason flags, DB identity, target size, file number, and sequence threshold. `TableBuilder` defines `Add`, `status`, `io_status`, `Finish`, `Abandon`, size/entry/property/checksum accessors, compaction hint, sequence-time mapping, and worker CPU reporting.

Control flow: factories consume these option structs when opening readers or constructing builders. Builder lifecycle requires monotonic `Add` calls, exactly one terminal `Finish` or `Abandon`, and destruction only after terminal handling.

State and persistence behavior: the header itself has no storage, but its interfaces define persistence metadata that table implementations emit into SST properties, checksums, identities, and file size accounting.

Dependencies/integration points: central integration surface for block-based, plain, cuckoo, external SST writer, compaction, table cache, compression manager, table property collectors, block cache tracing, and timestamp persistence.

Risks: many fields are references or non-owning pointers, so factories/builders must respect caller lifetimes. Misconfigured comparator, compression manager, timestamp persistence, or identity fields can produce unreadable or misleading SSTs. Builders are not internally synchronized for mutation.

Test signals: used by `SstFileWriter`, `SstFileDumper` compression estimation, and `table_reader_bench.cc`; concrete builder behavior is tested through table-format and external-SST tests.
