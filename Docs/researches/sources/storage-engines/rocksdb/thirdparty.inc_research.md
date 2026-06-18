# sources/storage-engines/rocksdb/thirdparty.inc

## Purpose

`thirdparty.inc` is a CMake include fragment for configuring optional third-party libraries, primarily for Windows/native package layouts rooted under `THIRDPARTY_HOME`. It wires compression, flags, and allocator dependencies into RocksDB build definitions.

## Important APIs, Types, and Functions

It sets `THIRDPARTY_LIBS`, `SYSTEM_LIBS`, and `ARTIFACT_SUFFIX`, and defines home/include/debug/release library variables for gflags, Snappy, LZ4, zlib, ZSTD, and jemalloc. Feature switches include legacy variables such as `GFLAGS`, `SNAPPY`, `LZ4`, `ZLIB`, `XPRESS`, and `JEMALLOC`, translated to `WITH_*` variables.

## Control Flow

CMake evaluates the file top to bottom. Each optional block checks whether the feature is enabled, lets environment variables override default include/library paths, adds compile definitions and include directories, and appends debug/optimized libraries to `THIRDPARTY_LIBS`. Disabled blocks emit status messages only.

## State and Persistence Behavior

There is no runtime persistence. Build state is persisted into the generated CMake configuration, compiler flags, link lines, and target names. Jemalloc changes `ARTIFACT_SUFFIX` to `_je`, affecting output artifact naming.

## Dependencies and Integration Points

The file integrates with top-level RocksDB CMake targets through `THIRDPARTY_LIBS`, `SYSTEM_LIBS`, include paths, and `add_definitions`. `XPRESS` links Windows `Cabinet.lib`; other features expect explicit `.lib` paths.

## Risks and Test Signals

Risks include stale hard-coded package paths, mismatched debug/release libraries, globally scoped include/definition leakage, and feature drift from modern `find_package` behavior. Test signals are configure-time status messages, successful Windows builds across enabled feature combinations, and link/runtime compression tests.
