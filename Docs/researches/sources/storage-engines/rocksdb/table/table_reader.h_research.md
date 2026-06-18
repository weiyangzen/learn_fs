# sources/storage-engines/rocksdb/table/table_reader.h

Purpose: declares the abstract `TableReader` interface for immutable persistent SST/table formats.

Important APIs/types/functions: pure virtual methods include `NewIterator`, `ApproximateOffsetOf`, `ApproximateSize`, `SetupForCompaction`, `GetTableProperties`, `ApproximateMemoryUsage`, and `Get`. Optional methods include range tombstone iterators, approximate key anchors, `Prepare`, `MultiGetFilter`, `MultiGet`, coroutine multiget, `Prefetch`, `DumpTable`, `VerifyChecksum`, and `MarkObsolete`. `Anchor` describes approximate user-key range anchors.

Control flow: callers open concrete readers through table factories, then use this uniform interface for point lookups, scans, metadata, checksum verification, dumping, and cache/compaction hints. Default `MultiGet` loops over keys and calls `Get`; specialized readers can override. Default optional features return no-op or `NotSupported`.

State and persistence behavior: the interface represents immutable persistent table data and requires thread-safe access. It stores no data itself but defines lifetime rules such as `ReadOptions` outliving returned iterators unless wrapped by higher layers.

Dependencies/integration points: central contract between DB/table cache/compaction/tooling and concrete table formats including block-based, plain, and cuckoo. Integrates `GetContext`, `MultiGetContext`, range tombstones, internal iterators, table properties, and table reader caller attribution.

Risks: implementers must honor arena allocation semantics for iterators and thread-safety for immutable access and `MarkObsolete`. Optional defaults can hide unsupported features unless callers check status. `skip_filters` semantics are format-specific.

Test signals: `sst_file_reader_test.cc` exercises concrete `TableReader` behavior through `SstFileReader`, including `Get`, `MultiGet`, `NewIterator`, `VerifyChecksum`, and table properties.
