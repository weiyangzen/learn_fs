# sources/storage-engines/rocksdb/examples/CMakeLists.txt

## Purpose
This CMake file declares build targets for the RocksDB example programs. It is a thin integration layer that compiles individual example source files and links them against the configured `${ROCKSDB_LIB}` target.

## Important APIs and control flow
The file calls `add_executable()` and `target_link_libraries()` for `simple_example`, `column_families_example`, `compact_files_example`, `c_simple_example`, `optimistic_transaction_example`, `transaction_example`, `compaction_filter_example`, `options_file_example`, and `multi_processes_example`. `multi_processes_example` is marked `EXCLUDE_FROM_ALL`, so it is available as a target but not built by default.

## State, dependencies, and integration
It depends on the parent CMake configuration defining `${ROCKSDB_LIB}` and include/link settings for the RocksDB library. The file contains no persistent state and no install/export logic; it only wires local examples into the build graph.

## Risks and test signals
The target list does not include `rocksdb_backup_restore_example.cc`, although the Makefile does, which can cause coverage differences between CMake and Make builds. No per-target C/C++ standard, warning, or platform settings are specified here, so correctness depends on inherited parent configuration. Test signals are a successful CMake configure/build for all listed targets and explicit build of the excluded multi-process target when needed.
