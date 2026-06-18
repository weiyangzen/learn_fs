# sources/storage-engines/rocksdb/tools/CMakeLists.txt

## Purpose

This CMake file defines RocksDB command-line tool targets built from `tools/` sources. It always builds core tools and conditionally builds additional utility/stress/dump tools when `WITH_TOOLS` is enabled.

## Important APIs, Types, and Functions

The main variables are `CORE_TOOLS`, `TOOLS`, `core_tool_deps`, and `tool_deps`. It creates executable targets from source basenames with optional `${ARTIFACT_SUFFIX}`, links core tools to `${ROCKSDB_LIB}`, links optional tools to `${ROCKSDB_LIB} ${THIRDPARTY_LIBS}`, and defines `ldb_tests` as a custom target running `ldb_tests.py`.

## Control Flow

CMake iterates over `sst_dump.cc` and `ldb.cc` unconditionally, then over optional sources such as `db_sanity_test.cc`, `write_stress.cc`, `db_repl_stress.cc`, `dump/rocksdb_dump.cc`, and `dump/rocksdb_undump.cc` inside `if(WITH_TOOLS)`.

## State and Persistence Behavior

There is no runtime state. Build graph state is persisted as generated executable targets and dependency lists.

## Dependencies and Integration Points

It depends on the parent CMake project defining `ROCKSDB_LIB`, `THIRDPARTY_LIBS`, `ARTIFACT_SUFFIX`, and `WITH_TOOLS`. The custom `ldb_tests` target integrates Python test execution with the `ldb` binary.

## Risks and Test Signals

Risks include target/list naming without suffix in dependency lists, missing third-party links for optional tools, and Python interpreter assumptions. Signals are successful CMake generation, tool linking, and `cmake --build . --target ldb_tests`.
