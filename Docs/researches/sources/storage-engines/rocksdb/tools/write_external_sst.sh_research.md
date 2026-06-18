# sources/storage-engines/rocksdb/tools/write_external_sst.sh

## Purpose

Shell helper that converts sorted input data files into external SST files using RocksDB's `ldb write_extern_sst` command.

## Important APIs, Control Flow, And Dependencies

The script requires an input data directory, DB path, and external SST output directory. It removes the DB directory, ensures the external SST directory exists, then iterates over files matching `sorted_data*` under the input directory. Each file is piped into `./ldb --db=<db> --create_if_missing write_extern_sst <sst_path>`, with output files named `extern_sst0`, `extern_sst1`, and so on.

## State, Persistence, Integration, Risks, And Test Signals

State changes are destructive for the target DB path because `rm -rf $db_dir` runs before writing. The generated SST files persist under the supplied external SST directory. Integration is through local `./ldb` and the input format expected by `write_extern_sst`. Risks include unquoted paths, unsorted `find` order, no cleanup of old external SST files, and destructive DB removal if arguments are wrong. Success is signaled by zero exit under `set -e`; any failed `ldb` invocation aborts.
