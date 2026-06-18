<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/types_util.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/utilities/types_util.h

Purpose: Declares helper APIs for converting between user-facing keys and raw-table internal key records, plus parsing internal table iterator keys back into structured entry metadata. This is a small public utility surface for tools that need to inspect SST/raw table contents without depending on internal headers.

Important APIs/types/functions: `GetInternalKeyForSeek`, `GetInternalKeyForSeekForPrev`, and `ParseEntry` all return `Status`, accept the column-family/table `Comparator`, and use `Slice`/`std::string`/`ParsedEntryInfo` from RocksDB public types.

Control flow: The header only declares functions; implementations are expected to encode a seek boundary for forward or reverse raw-table iteration, or decode an internal key from a table iterator. Callers pass the same comparator used to create the column family or SST writer so timestamp or custom-comparator semantics match the table.

State and persistence behavior: No persistent state is owned here. The generated internal key is written into caller-owned `buf`; `ParseEntry` fills caller-owned `ParsedEntryInfo`. Misusing a comparator can make seek boundaries or parsed entries disagree with persisted table encoding.

Dependencies and integration points: Depends on `rocksdb/comparator.h`, `slice.h`, `status.h`, and `types.h`. It integrates with raw table iterators, `SstFileWriter`, and offline table inspection/repair tools.

Risks and edge cases: Comparator mismatch is the main correctness risk, especially with custom comparators or user-defined timestamps. Since these utilities handle internal key bytes, malformed input should be expected to return non-OK status rather than be trusted.

Test signals: Useful coverage would seek raw table iterators using generated keys, validate reverse seek behavior, and feed valid/corrupt internal keys into `ParseEntry` under bytewise and custom comparator configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/types_util.h -->
