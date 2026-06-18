<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ingest_external_sst.sh -->
# sources/storage-engines/rocksdb/tools/ingest_external_sst.sh

## Purpose
This small Bash helper ingests every external SST file matching `extern_sst*` from a directory into a RocksDB database using `ldb ingest_extern_sst`.

## Important APIs, Types, and Functions
- Positional arguments are `<DB Path> <External SST Dir>`.
- The file discovery command is ``find $external_sst_dir -name extern_sst*``.
- Each file is ingested through `./ldb --db=$db_dir --create_if_missing ingest_extern_sst $f`.

## Control Flow
The script validates that at least two arguments are present, assigns `db_dir` and `external_sst_dir`, loops over matching files produced by `find`, prints a status line for each, and runs the `ldb` ingestion command. There is no explicit `set -e`, so failures do not necessarily stop later iterations.

## State and Persistence Behavior
The destination DB is created if missing and modified by each external SST ingestion. The script does not delete or move source SST files, does not compact after ingestion, and does not clean up a partially ingested DB on failure.

## Dependencies and Integration Points
Dependencies are Bash, `find`, and a `./ldb` binary in the current working directory. It integrates with RocksDB's external SST ingestion command exposed by `ldb`.

## Risks and Edge Cases
- Paths are unquoted, so whitespace in DB or SST paths breaks the command.
- The glob-like `extern_sst*` pattern is passed unquoted to `find`; shell expansion in the current directory can alter behavior.
- No `set -e` or return-code accumulation means the script may exit zero even if an ingestion fails before a later successful command.
- It assumes `./ldb`, not a configurable path.

## Test Signals
There is no formal test. Runtime signals are printed "Ingesting" lines and `ldb` exit messages. Callers should inspect command exit codes if robust automation is needed.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ingest_external_sst.sh -->
