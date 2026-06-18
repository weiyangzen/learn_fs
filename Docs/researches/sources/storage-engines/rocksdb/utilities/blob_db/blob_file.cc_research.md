## `sources/storage-engines/rocksdb/utilities/blob_db/blob_file.cc`

Purpose: implements `BlobFile`, the in-memory handle for one persisted BlobDB log file. It owns metadata, optional append writer, cached random access reader, footer/header parsing, immutability/obsolete transitions, and file-state diagnostics.

Important APIs and functions: constructors initialize existing-file or new-file metadata. `PathName()` derives the absolute blob filename. `DumpState()` emits a debug summary. `MarkObsolete()` stores obsolete sequence. `WriteFooterAndCloseLocked()` appends `BlobLogFooter`, marks the file immutable, updates file size, and drops the writer. `ReadFooter()` reads and decodes the footer using the cached reader. `Fsync()` syncs the writer if present. `CloseRandomAccessLocked()` drops the cached reader. `GetReader()` lazily opens and caches a `RandomAccessFileReader`. `ReadMetadata()` reads file size, header, and optional footer from persistent storage.

Control flow: new mutable files are created by `BlobDBImpl`, then writers append records. On close, the footer captures blob count and TTL expiration range, then the writer is reset. On reads, `GetReader()` first tries a read lock for an existing reader, then upgrades to a write lock to open one exactly once. On DB open, `ReadMetadata()` validates the header, marks header state, then decodes a footer if the file is large enough and the footer is valid; absent/malformed footer is tolerated as an open/incomplete file state.

State and persistence behavior: persistent fields are represented by blob file path/number, header column family id, compression, TTL flag/range, record count, file size, and footer fields. In-memory-only fields include linked SST file set, writer, reader, closed flag, immutable/obsolete sequence numbers, access timestamp, and validity flags. `BlobRecordAdded()` increments count and file size after physical record append.

Dependencies and integration: uses blob log format/writer, `BlobFileName`, `RandomAccessFileReader`, file system APIs, readahead support, logging, DB format sequence numbers, and `BlobDBImpl` for friendship and file options.

Risks: destructor attempts to delete obsolete files through `Env::Default()` as a fallback, which can differ from the DB env. Header corruption during open is fatal/corrupt; footer corruption is tolerated, so later logic must handle missing footer counts. Reader caching affects open file count in `BlobDBImpl`; stale counts can arise if readers are closed outside expected paths. Per-file methods rely on external locking comments rather than internal enforcement for several transitions.

Test signals: BlobDB tests inspect file number, TTL flag/range, size, immutability, obsolete state, linked SSTs, reader lifecycle indirectly, footer sync counters, and metadata across reopen/trash scenarios.
