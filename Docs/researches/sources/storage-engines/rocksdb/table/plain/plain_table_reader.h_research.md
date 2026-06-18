# sources/storage-engines/rocksdb/table/plain/plain_table_reader.h

Purpose: declares the `PlainTableReader` table-reader implementation and its file-info helper for RocksDB plain-table SSTs.

Important APIs/types/functions: `PlainTableReaderFileInfo` records mmap mode, mmapped data, logical data end offset, and the owned `RandomAccessFileReader`. `PlainTableReader` derives from `TableReader` and exposes `Open`, `NewIterator`, `Prepare`, `Get`, approximate size/offset methods, `SetupForCompaction`, `GetTableProperties`, and `ApproximateMemoryUsage`. Protected and private helpers cover bloom matching, index population, mmap setup, record decoding, offset lookup, and prefix extraction.

Control flow: the header makes `Open` the only factory-style construction path, with constructor public but specialized for callers already holding properties. Query flow is organized around prefix extraction, bloom check, index offset lookup, and `Next` record decoding. Iterator access is granted through friendship to `PlainTableIterator`.

State and persistence behavior: persistent reader state includes comparator, encoding type, status, index, full-scan flag, fixed or variable user-key length, prefix extractor pointer, bloom, file info, arena-backed allocations, immutable options reference, optional cleanable, file size, and shared table properties. `data_start_offset_` is fixed at zero, and `data_end_offset_` comes from table properties.

Dependencies/integration points: the API sits between RocksDB's generic `TableReader` contract and plain-table-specific components from `table/plain`. It also uses `TableCache` friendship, `GetContext`, `InternalKeyComparator`, and table property metadata.

Risks: lifetime is important: `prefix_extractor_` and `ioptions_` are non-owning references/pointers and must outlive the reader as expected by RocksDB option lifetimes. Full-scan and total-order modes have different capabilities. Fixed-key length logic assumes internal-key trailers are eight bytes.

Test signals: exposed methods are used by plain table factory/open paths and by higher-level SST tooling. The listed tests mainly validate generic reader behavior through `SstFileReader`, not this header directly.
