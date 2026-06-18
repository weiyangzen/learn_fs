# sources/storage-engines/rocksdb/table/sst_file_dumper.h

Purpose: declares the `SstFileDumper` utility class for SST inspection, dumping, checksum verification, property reads, and compression-size experiments.

Important APIs/types/functions: constructor accepts RocksDB `Options`, file name, file temperature, readahead size, checksum/output/decode flags, `EnvOptions`, silence mode, and sequence-number display flag. Public methods include `ReadSequential`, `ReadTableProperties`, `VerifyChecksum`, `DumpTable`, `ShowAllCompressionSizes`, `ShowCompressionSize`, `GetReadNumber`, `GetInitTableProperties`, `getStatus`, and `GetMetaIndexContents`.

Control flow: the header separates initialization (`GetTableReader`, `ReadTableProperties`, `SetTableOptionsByMagicNumber`, `NewTableReader`) from inspection operations. `ReadSequential` can limit count, bound by from/to keys, or treat `from` as a prefix.

State and persistence behavior: object state caches options, immutable/mutable options, read options, comparator, table properties, meta-index block contents, the open file reader, table reader, file temperature, output flags, and count of sequentially read entries.

Dependencies/integration points: it bridges public utility commands to table internals (`TableReader`, `TableBuilderOptions`, `BlockContents`, `RandomAccessFileReader`) and RocksDB option structures.

Risks: callers must check `getStatus()` or public method statuses because construction performs real IO. `GetInitTableProperties()` returns a raw pointer owned by the dumper. Output modes can affect stdout/stderr but not stored state.

Test signals: no direct tests in this subset; behavior is validated by utility tests and by table-reader tests that share the same table-reader contracts.
