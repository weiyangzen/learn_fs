# sources/storage-engines/rocksdb/table/sst_file_writer.cc

Purpose: implements `SstFileWriter`, the API for creating external SST files that can later be read or ingested by RocksDB.

Important APIs/types/functions: static external property names define version and global sequence number keys. `SstFileWriter::Rep` owns the file writer, table builder, options, comparator, file metadata, timestamp policy, and helper methods `AddImpl`, timestamp-aware `Add`, `AddEntity`, `DeleteRangeImpl`, timestamp-aware `DeleteRange`, and `InvalidatePageCache`. Public methods include `Open`, `Put`, `PutEntity`, `Merge`, `Delete`, `DeleteRange`, `Finish`, `FileSize`, and `CreatedBySstFileWriter`.

Control flow: `Open` creates a writable file with no-reopen/no-reader contract, selects compression from bottommost/per-level/default options, builds internal property collector factories including external-SST metadata, constructs `TableBuilderOptions`, wraps the file in `WritableFileWriter`, and creates the table builder. Add/delete paths validate open state, builder status, key/value sizes, timestamp compatibility, strict key ordering, and value type before encoding internal keys and adding to the builder. `Finish` rejects empty files, finishes and syncs/closes the builder/file, records checksums, deletes failed files, optionally strips timestamps from returned metadata, and releases the builder.

State and persistence behavior: persistent output is an SST file plus `ExternalSstFileInfo` metadata. In-memory state tracks smallest/largest point and range-delete keys, entry counts, file size, checksum, fake DB/session identity, and fake file numbers for cache-key uniqueness. Destructor abandons an unfinished builder.

Dependencies/integration points: integrates with `WritableFileWriter`, `TableBuilder`, `TableBuilderOptions`, table-property collectors, wide-column serialization, range tombstones, DB session ID generation, file checksum handoff, environment/file-system APIs, and external file ingestion metadata.

Risks: keys must be strictly ascending according to the configured user comparator including timestamp ordering. Timestamp-aware comparators reject timestamp-less APIs; non-persisted timestamp mode accepts only minimum timestamps. Failed finish deletes the target file but ignores delete failures. Page-cache invalidation is best-effort and treats unsupported as OK.

Test signals: `sst_file_reader_test.cc` covers basic writer output, timestamp ordering/mismatch, non-persisted timestamp rules and metadata stripping, empty/corrupt property implications via reader checks, and external-SST global sequence compatibility.
