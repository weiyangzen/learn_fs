## `sources/storage-engines/rocksdb/utilities/cache_dump_load.cc`

Purpose: provides public factory functions for default cache dump/load components. It bridges the `rocksdb/utilities/cache_dump_load.h` API to concrete file-backed readers/writers and default dumper/loader implementations.

Important APIs and functions: `NewToFileCacheDumpWriter()` creates a `WritableFileWriter` for a named file and wraps it in `ToFileCacheDumpWriter`. `NewFromFileCacheDumpReader()` creates a `RandomAccessFileReader` and wraps it in `FromFileCacheDumpReader`. `NewDefaultCacheDumper()` allocates `CacheDumperImpl`. `NewDefaultCacheDumpedLoader()` allocates `CacheDumpedLoaderImpl`.

Control flow: each factory constructs the lower-level file reader/writer first and returns early on I/O status failure. Ownership is moved into the concrete wrapper through `std::unique_ptr`. The dumper/loader factories are status-only constructors and do not perform dump/load work themselves.

State and persistence behavior: the writer factory creates/opens a dump target file; the reader factory opens an existing dump file. No cache entries are serialized here; persistence format is implemented by `cache_dump_load_impl.*`.

Dependencies and integration: depends on RocksDB public cache dump/load declarations, `WritableFileWriter`, `RandomAccessFileReader`, env/file system/file options, table options, and the implementation header. These functions are likely the public extension points used by tools or DB warmup paths.

Risks: factories do not validate null output pointer arguments. They pass `nullptr` tracing/rate-limiter contexts to file reader/writer creation. `NewDefaultCacheDumpedLoader()` accepts `BlockBasedTableOptions` but the current implementation ignores it, which can surprise callers expecting table-option-specific behavior.

Test signals: no listed direct tests; behavior would be covered by cache dump/load tests elsewhere if present.
