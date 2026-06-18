<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dump/rocksdb_undump.cc -->
# sources/storage-engines/rocksdb/tools/dump/rocksdb_undump.cc

## Purpose
`rocksdb_undump.cc` is the command-line frontend for `DbUndumpTool`. It parses source dump and destination DB paths, optional compaction, and optional RocksDB open options, then loads dump records into a DB.

## Important APIs, Types, and Functions
- gflags: `--dump_location`, `--db_path`, `--compact`, and `--db_options`.
- `GetOptionsFromString()` parses DB options.
- `UndumpOptions` carries `db_path`, `dump_location`, and `compact_db`.
- `DbUndumpTool::Run()` performs the actual format validation, record reads, writes, and optional compaction.

## Control Flow
Under gflags, `main()` parses flags, requires both `--db_path` and `--dump_location`, populates `UndumpOptions`, parses `--db_options` if present, invokes `DbUndumpTool`, and returns one on failure. Without gflags, it builds a fallback executable that reports the missing dependency.

## State and Persistence Behavior
The wrapper causes records from the dump file to be written into the DB at `--db_path`; the underlying implementation opens the DB with `create_if_missing=true`. It does not destroy any existing DB, so loading into a populated DB can overwrite matching keys and leave unrelated keys intact. `--compact` triggers full-range compaction after load.

## Dependencies and Integration Points
This file depends on the same gflags and options-string utilities as `rocksdb_dump.cc` and integrates shell usage with `DbUndumpTool`.

## Risks and Edge Cases
- Existing destination DB contents are not cleared.
- Custom DBs requiring non-string-parseable factories may not be openable through `--db_options`.
- Input format validation and truncation behavior are owned by `DbUndumpTool`, not the wrapper.

## Test Signals
Exit code zero means all records were loaded and optional compaction succeeded. Exit code one means missing flags, parse failure, invalid dump input, DB write/open failure, or compaction failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dump/rocksdb_undump.cc -->
