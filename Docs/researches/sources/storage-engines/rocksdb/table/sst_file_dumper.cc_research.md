# sources/storage-engines/rocksdb/table/sst_file_dumper.cc

Purpose: implements `SstFileDumper`, the utility-facing reader for inspecting SST files, verifying checksums, dumping key/value content, reading table properties, and estimating compression-size outcomes.

Important APIs/types/functions: constructor initializes read options and immediately calls `GetTableReader`. `GetTableReader` opens the file, reads footer/properties/meta-index, selects the right table factory, recreates mmap-capable files for plain/cuckoo formats, configures comparators from table properties, and constructs the `TableReader`. `ReadSequential`, `ReadTableProperties`, `VerifyChecksum`, `DumpTable`, `ShowAllCompressionSizes`, `ShowCompressionSize`, `CalculateCompressedTableSize`, `SetTableOptionsByMagicNumber`, and `NewTableReader` provide the public behaviors.

Control flow: file open checks emptiness, tail-prefetches for footer reading, uses the magic number to load properties and select format-specific options, then opens a table reader. Sequential scan creates an internal iterator, optionally seeks to `from`, applies timestamp-normalized range bounds, parses internal keys, prints values according to type, and verifies scanned count against properties for full scans. Compression reporting rewrites the existing table into a memory-env SST for each compression setting and times write/read passes.

State and persistence behavior: owns the target `RandomAccessFileReader`, `TableReader`, cached `TableProperties`, meta-index contents, mutable options, read options, comparator, output settings, and `read_num_`. It does not mutate the source SST except by reading it; compression-size estimates write temporary in-memory files.

Dependencies/integration points: integrates with `Footer`, `ReadTableProperties`, `ReadMetaIndexBlockInFile`, table factories, block-based/plain/cuckoo formats, blob index decoding, wide-column serialization, compression manager/statistics, `NewMemEnv`, and ldb tooling conventions.

Risks: format selection depends on valid magic number and properties; unsupported formats return invalid argument. Plain/cuckoo need mmap reads. `ReadSequential` skips unparsable keys but continues printing. Count verification subtracts range deletions but does not verify range tombstone contents. Compression-size code assumes iterator output can be rebuilt through a block-based builder.

Test signals: exercised by SST dump CLI/tool tests outside this subset; listed code overlaps with `SstFileReader` tests for checksum, properties, and iterator correctness.
