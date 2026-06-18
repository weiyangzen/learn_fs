# sources/storage-engines/wiredtiger/bench/wtperf/CMakeLists.txt

## Purpose
This CMake file builds the `wtperf` benchmark executable and registers a small-btree smoke variant for CTest/check.

## Important APIs, Types, and Functions
It constructs `wt_perf_flags` based on enabled compression libraries, passing compile definitions for Snappy, LZ4, Zlib, and Zstd extension paths. It calls `create_test_executable(wtperf SOURCES ...)` with wtperf implementation files and `define_test_variants(wtperf ...)` for `small_btree`.

## Control Flow
Configure-time branches append flags when compressor options are enabled. The executable includes config parsing, idle table cycle, misc helpers, tracking, main workload, throttle, and truncate modules. The test variant runs `wtperf -O runners/small-btree.wtperf -o run_time=20`.

## State and Persistence Behavior
No direct runtime state. It controls build graph state, compile flags, and test registration.

## Dependencies and Integration Points
It depends on repository CMake helper macros, compressor build options, all listed C sources, and runner config files. It integrates `wtperf` into CI labels `check` and `wtperf`.

## Risks and Edge Cases
Compile-time extension path definitions must match installed/built extension layout. The smoke variant relies on source directory paths and helper macro quoting. Missing optional compressors should not define stale paths.

## Test Signals
Successful build of `wtperf` and a passing `small_btree` CTest variant are the main signals. Compressor-enabled builds should verify the corresponding flags appear in compile commands.
