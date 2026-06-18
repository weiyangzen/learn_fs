# sources/storage-engines/rocksdb/tools/sst_dump_test.cc

## Purpose
This GoogleTest suite validates `SSTDumpTool` and related `SstFileDumper` behavior. It creates synthetic SST files and verifies raw dumps, scans/checks, recompression, compression managers, memory environments, readahead sizing, file path validity, mmap reads, meta-block listing, and record-count verification.

## Important APIs, Types, and Functions
Helpers include `MakeKey`, `MakeKeyWithTimeStamp`, `MakeValue`, `MakeWideColumn`, and `cleanup`. `SSTDumpToolTest` manages a temp directory/env, owns `PopulateCommandArgs`, `createSST`, and `SSTDumpToolTestCase`. `MyManager` is a custom `CompressionManager` for dependency-injection testing. Tests use `TableBuilder`, `BlockBasedTableFactory`, `SstFileDumper`, `SyncPoint`, `SaveAndRestore`, and `ObjectLibrary`.

## Control Flow
Tests build SST files by writing internal keys to a `TableBuilder`, then invoke `SSTDumpTool::Run` with constructed argv arrays. Generic cases cover `raw`, `show_properties`, `recompress`, `verify`, and `list_meta_blocks`. Path tests run combinations of missing files, valid SSTs, directories, text files, fake SSTs, and `--` argument handling. Record verification tests intentionally corrupt table property counts through `SyncPoint` and verify corruption is reported only for full scans without range/read limits.

## State and Persistence
The suite writes temporary `.sst` and `_dump.txt` files under a per-thread test directory, cleaning them unless `KEEP_DB` is set. It can register a custom compression manager in the default object library, which is process-global test state.

## Dependencies and Integration Points
It integrates table building, block-based table options, wide-column serialization, custom comparators, timestamp comparators, compression infrastructure, env/mem-env support, file readers, and the public dump tool.

## Risks
The tests allocate argv buffers manually and rely on exact command aliases, output file naming, and sync-point names. The custom compression-manager test is conditional on codec support. Path-validity expectations distinguish single invalid file failure from mixed valid/invalid success, which should remain documented.

## Test Signals
Passing tests indicate that the dump tool can parse options, identify valid SSTs, dump/read/recompress tables, handle env variants, honor readahead, and detect entry-count mismatches.
