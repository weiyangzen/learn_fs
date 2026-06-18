## `sources/storage-engines/rocksdb/utilities/blob_db/blob_file.h`

Purpose: declares `BlobFile`, the central metadata and I/O handle for BlobDB log files. It captures persistent blob-log identity and transient access state while exposing controlled lifecycle methods to `BlobDBImpl` and compaction filters.

Important APIs and types: public methods include constructors, destructor, `PathName`, `BlobFileNumber`, SST link/unlink accessors, `BlobCount`, `DumpState`, `Immutable`, `MarkImmutable`, immutable/obsolete sequence accessors, `MarkObsolete`, `Fsync`, `GetFileSize`, expiration accessors, TTL flag accessors, writer getter, `ReadMetadata`, and `GetReader`. Private methods include `ReadFooter`, `WriteFooterAndCloseLocked`, `CloseRandomAccessLocked`, `SetFromFooterLocked`, setters, and `BlobRecordAdded`.

Control flow represented by declarations: `BlobDBImpl` creates a new file with header metadata, appends records through a writer, closes it by footer append, and later opens random readers for reads. GC and TTL eviction mark immutable files obsolete; deletion waits until no active snapshots can see them. SST link sets are maintained when GC is enabled to know whether old non-TTL files can be obsoleted.

State and persistence behavior: fields include immutable identity (`path_to_dir_`, `file_number_`), persistent/log-derived metadata (`column_family_id_`, `has_ttl_`, `expiration_range_`, `blob_count_`, `file_size_`, `header_`), lifecycle state (`closed_`, `immutable_sequence_`, `obsolete_`, `obsolete_sequence_`), and transient resources (`log_writer_`, `ra_file_reader_`, `last_access_`). Header/footer validity flags track recovery quality.

Dependencies and integration: includes blob log format/writer, random access file reader, RocksDB env/file system/options, port mutexes, and friendship with `BlobDBImpl`, comparators, and blob-index compaction filters.

Risks: the class exposes several atomic getters without locks but other fields require caller-held locks; this mixed model can be misused. `linked_sst_files_` is not internally synchronized. Obsolete implies immutable by assertion, so any path that marks a mutable file obsolete must close it first. TTL range extension mutates a pair directly and requires a file lock externally.

Test signals: file state is directly checked throughout `blob_db_test.cc`, especially GC mapping, TTL eviction, deletion disable, and live metadata tests.
