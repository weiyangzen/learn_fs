<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ldb.cc -->
# sources/storage-engines/rocksdb/tools/ldb.cc

## Purpose
`ldb.cc` is the standalone entry point for RocksDB's `ldb` command-line tool. It constructs an `LDBTool` and delegates all command parsing and execution to `RunAndReturn()`.

## Important APIs, Types, and Functions
- Includes `rocksdb/ldb_tool.h`.
- `main(int argc, char** argv)` creates `ROCKSDB_NAMESPACE::LDBTool tool` and returns `tool.RunAndReturn(argc, argv)`.

## Control Flow
All runtime behavior is delegated to the library tool implementation. This wrapper has no local flag parsing, validation, or command dispatch.

## State and Persistence Behavior
State and persistence depend entirely on the selected `ldb` subcommand, such as load, get, put, delete, scan, dump, or ingestion commands. The wrapper itself owns no state.

## Dependencies and Integration Points
The file integrates the `LDBTool` library class into an executable. Scripts in this subset (`generate_random_db.sh` and `ingest_external_sst.sh`) depend on this executable for loading data, deleting ranges or keys, and ingesting external SSTs.

## Risks and Edge Cases
The wrapper is intentionally thin; any risks live in `LDBTool` or callers. Build/link failures are the main local risk because the entry point requires the ldb tool library.

## Test Signals
There are no local tests. Operational signal is the exit code returned from `LDBTool::RunAndReturn()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ldb.cc -->
