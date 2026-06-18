## sources/storage-engines/rocksdb/table/block_based/block_prefetcher.cc

Purpose: implements block read-ahead policy for block-based table reads. It chooses between filesystem prefetch and RocksDB `FilePrefetchBuffer`, handling compaction readahead, explicit user readahead, implicit sequential auto-readahead, direct I/O, async prefetch buffering, and cache-tier reads that disallow I/O.

Important API/function: `BlockPrefetcher::PrefetchIfNeeded()` takes the table representation, current block handle, requested readahead size, compaction flag, sequential-check bypass flag, read options, optional callback for readahead sizing, and async prefetch mode.

Control flow: the method returns immediately for `kBlockCacheTier`. For compaction, it uses filesystem prefetch when supported and direct I/O is off; otherwise it creates an internal prefetch buffer using compaction readahead settings. For normal reads, explicit user `readahead_size` always creates a user-scan prefetch buffer. Implicit auto-readahead first checks max/initial settings, then either bypasses sequential checks or tracks offsets to require sequential reads before prefetching. With filesystem prefetch support it calls `RandomAccessFileReader::Prefetch`, records `readahead_limit_`, and doubles `readahead_size_` up to the configured maximum. Unsupported or unavailable filesystem prefetch falls back to `FilePrefetchBuffer`.

State and persistence behavior: no persistent state. Runtime state includes previous block offset/length, file read count, current readahead size, readahead limit, initial auto size, compaction size, and a lazily created prefetch buffer. `ResetValues()` resets auto-readahead after non-sequential access.

Dependencies/integration points: depends on `BlockBasedTable::Rep`, `BlockHandle`, table options, `RandomAccessFileReader`, filesystem supported operations, `ReadOptions`, `ReadaheadParams`, and `FilePrefetchBuffer` usage labels.

Risks: incorrect sequential detection can under-prefetch scans or over-prefetch random reads. Filesystems may advertise prefetch but return `NotSupported`, so fallback correctness matters. Direct I/O requires internal buffering. Async mode changes buffer count and may affect stats timing.

Test signals: `block_based_table_reader_test.cc` validates `fs_prefetch_support` initialization and has a disabled async MultiScan test covering coalesced reads, cached-block exclusion, and prefetch limits. MultiScan prefetch-limit tests cover higher-level effects.
