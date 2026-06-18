# sources/storage-engines/rocksdb/tools/sst_dump_tool.cc

## Purpose
This file implements `SSTDumpTool::Run`, the core logic for the `sst_dump` command. It parses CLI options, discovers SST files from files/directories, configures env/table/compression options, invokes `SstFileDumper`, and performs scan/check/raw/verify/recompress/identify/property/meta-block operations.

## Important APIs, Types, and Functions
`print_help()` emits usage and supported compression types. `ParseIntArg()` parses integer flags and exits on malformed numeric input. `SSTDumpTool::Run()` owns all command parsing and execution. It uses `Env::CreateFromUri`, `OptionsHelper::compression_type_string_map`, `CompressionManager::CreateFromString`, `LDBCommand::HexToString`, `ParseInternalKey`, `SstFileDumper::ReadSequential`, `DumpTable`, `VerifyChecksum`, `ShowAllCompressionSizes`, `ReadTableProperties`, and meta-index block iteration.

## Control Flow
`Run()` initializes defaults, registers custom compression managers, parses arguments, validates paired compression-level flags and prefix/from conflicts, decodes hex range keys, and requires at least one file or directory. It expands directories by listing children, filters to `.sst`, constructs an `SstFileDumper` for each valid SST, optionally filters by property regexes, then executes the selected command. It accumulates summary counters and valid SSTs. At the end it prints identify results when requested and returns failure if no valid SST files were found.

## State and Persistence
Most commands are read-only. `raw` writes `<sst_basename>_dump.txt`. `recompress` simulates table output sizes and mutates local `Options` table/compression settings before each file. Summary counters track file/block/size totals in memory.

## Dependencies and Integration Points
It depends on RocksDB env creation, table factories, block contents, compression managers, db_stress compression registration, and ldb hex parsing. It is called by `sst_dump.cc` and directly by `sst_dump_test.cc`.

## Risks
The parser is manual and mixes `exit(1)` with returned error codes, which can surprise embedders. Some boolean parsing accepts only first-character truthiness. Directory expansion scans direct children only. `--command=verify_checksum` appears accepted by tests through behavior equivalent to validation paths, although help lists `verify`. Mutating `options` inside the per-file loop can affect later files. Regex filters are intentionally niche and depend on property string formatting.

## Test Signals
`sst_dump_test.cc` covers help/version, raw dumps, recompression, custom compression manager, mem env, readahead, path validity, mmap reads, and record-count mismatch detection.
