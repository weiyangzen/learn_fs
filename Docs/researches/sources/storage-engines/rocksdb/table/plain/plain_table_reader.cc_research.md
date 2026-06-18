# sources/storage-engines/rocksdb/table/plain/plain_table_reader.cc

Purpose: implements `PlainTableReader`, RocksDB's table reader for plain-table SSTs, including open-time property validation, optional mmap setup, index and bloom initialization, point lookup, and forward iteration over encoded records.

Important APIs/types/functions: `PlainTableReader::Open` reads table properties, validates prefix extractor compatibility unless full-scan mode is requested, resolves encoding, builds the reader, optionally populates the index, and stores properties. `PopulateIndex`, `PopulateIndexRecordList`, `AllocateBloom`, and `FillBloom` build or load the plain table hash/sub-index and bloom data. `GetOffset`, `Next`, `Get`, and `Prepare` are the lookup path. The local `PlainTableIterator` implements `InternalIterator` with `SeekToFirst`, prefix-aware `Seek`, and forward `Next`; reverse operations are unsupported.

Control flow: opening rejects oversized files, reads table properties, mmaps the whole file when requested, then either builds/loads index metadata or marks `full_scan_mode_`. Lookups compute a total-order full-key hash or prefix hash, consult bloom, find a candidate offset through direct bucket lookup or sub-index binary search, then scan forward until the target internal key is reached or the prefix changes. Iterator seek follows the same offset lookup, then advances until the first key greater than or equal to the target.

State and persistence behavior: source data is immutable SST file content referenced by `PlainTableReaderFileInfo`. Index and bloom allocations are held by `Arena` and cache allocation pointers, while `table_properties_` persists read metadata for callers. `dummy_cleanable_` is used for immortal mmap tables when values can reference file-backed memory.

Dependencies/integration points: integrates with `ReadTableProperties`, `ReadMetaBlock`, `PlainTableKeyDecoder`, `PlainTableIndexBuilder`, `PlainTableBloomV1`, RocksDB `GetContext`, perf counters, and `TableReader` callers. It depends heavily on a correct `SliceTransform` matching the file's stored prefix extractor name.

Risks: full-scan mode intentionally disables `Get` and `Seek`; reverse iteration is asserted/not supported. Prefix extractor mismatch is a hard error except in full scan. Corrupt offsets, non-seekable first keys, malformed internal keys, or index/data disagreement surface as `Status::Corruption`/parse errors. Approximate offset/size return zero, so consumers must not rely on meaningful size estimates for plain tables.

Test signals: behavior is indirectly exercised by table reader benchmarks, SST dumper paths that open plain tables in full-scan mode, and plain-table format tests elsewhere. This file itself has no local unit tests in the listed subset.
