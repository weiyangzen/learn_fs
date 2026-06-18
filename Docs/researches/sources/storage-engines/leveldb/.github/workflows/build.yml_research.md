<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/leveldb/.github/workflows/build.yml -->
# sources/storage-engines/leveldb/.github/workflows/build.yml

## Purpose
GitHub Actions CI matrix for LevelDB across Linux/macOS/Windows, clang/gcc/msvc, and Debug/RelWithDebInfo builds.

## Important APIs, Types, And Functions
Workflow keys include `on: [push, pull_request]`, read-only contents permission, one `build-and-test` job, matrix `compiler`, `os`, and `optimized`, and environment variables for CMake build type/path and executable suffix.

## Control Flow
Checkout submodules, install Linux dependencies, configure CMake with an install prefix, build, run `ctest`, run LevelDB benchmarks, conditionally run SQLite/Kyoto Cabinet benchmarks, then test the install target.

## State And Persistence Behavior
Persists only CI build artifacts in `${{ github.workspace }}/build` and an install test prefix under `${{ runner.temp }}`. Matrix exclusions encode platform/compiler support.

## Dependencies And Integration Points
Depends on GitHub Actions hosted runners, CMake, submodules, libkyotocabinet-dev, libsnappy-dev, and libsqlite3-dev on Linux. Directly validates `CMakeLists.txt`, benchmark targets, unit tests, and install/package rules used by downstream consumers.

## Risks
Actions use `checkout@v2`; Linux package availability can affect Kyoto/SQLite benchmark coverage; Windows skips SQLite and Kyoto Cabinet benchmarks.

## Test Signals
The workflow itself is the test signal: `ctest --verbose`, `db_bench`, `db_bench_sqlite3` off Windows, `db_bench_tree_db` on Linux clang, and install target build.
<!-- END_FILE_RESEARCH: sources/storage-engines/leveldb/.github/workflows/build.yml -->
