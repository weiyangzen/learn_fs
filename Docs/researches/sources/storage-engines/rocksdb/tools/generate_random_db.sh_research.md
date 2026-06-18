<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/generate_random_db.sh -->
# sources/storage-engines/rocksdb/tools/generate_random_db.sh

## Purpose
This Bash script loads pre-generated text data into a RocksDB database using the `ldb load` command while varying compression settings and optionally adding deterministic range tombstones or point deletes. It is used to generate DBs with mixed feature coverage for compatibility and testing.

## Important APIs, Types, and Functions
- Positional arguments are `<input_data_path> <DB Path> [<ldb_command>]`.
- `ldb_cmd` defaults to `./ldb`.
- Feature probes use `ldb --version`, a trial `ldb load --compression_type=mixed`, and `ldb --help | grep deleterange`.
- `compression_opts` starts with `no`, `snappy`, `zlib`, and `bzip2`, and expands to include `zstd`, `lz4`, `lz4hc`, and maybe `mixed`.
- Per-file deterministic deletion decisions use `md5sum`, `wc -l`, `sed`, and shell arithmetic.

## Control Flow
The script validates argument count, removes the target DB directory, probes `ldb` feature support, builds the compression list, enables `set -e`, seeds `n` from `$RANDOM`, and loops over every file from `ls -1 $input_data_dir`. For each file it chooses compression and dictionary byte settings from `n`, loads the file with `ldb load --auto_compaction=false --create_if_missing`, then uses the file hash to decide whether to delete a small key range. If `deleterange` is supported it creates a range tombstone from `key` to `key0`; otherwise it deletes the chosen key. It increments `n` after every file.

## State and Persistence Behavior
The script deletes the target DB at startup and creates a new one through `ldb`. Loaded data may remain in WALs until a later recovery because auto compaction is disabled. That behavior is intentional so generated DBs cover WAL format compatibility in addition to SST/table compatibility. Range tombstones or point deletes alter the logical contents deterministically based on input file hashes.

## Dependencies and Integration Points
Dependencies are Bash, `ldb`, `md5sum`, `grep`, `wc`, `sed`, and standard Unix tools. It integrates with `ldb load`, `ldb deleterange`, and `ldb delete`, and probes feature support for newer compression options.

## Risks and Edge Cases
- The script uses unquoted paths in several commands, so spaces or glob characters in input or DB paths can fail.
- Iterating `for f in \`ls -1\`` is not safe for filenames containing whitespace.
- `rm -rf $db_dir` is destructive and unquoted.
- `$RANDOM` makes compression assignment non-reproducible unless the shell seed is controlled, while deletion choice is deterministic per file.
- Dictionary compression support is inferred crudely from `ldb --version`.

## Test Signals
There is no formal test. Observable signals are echoed load/delete messages and successful completion under `set -e`. Any failing `ldb`, checksum, or file command aborts the script.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/generate_random_db.sh -->
