# sources/storage-engines/foundationdb/flow/config.h.cmake

Purpose: CMake-generated configuration header template for Flow/FoundationDB compilation flags and build paths.

Important APIs/types/functions: `#cmakedefine` entries for allocation instrumentation, debug/release, IDE mode, sanitizers, GCOV, Valgrind, DTrace, aligned allocation, and jemalloc; path macros `FDB_SOURCE_DIR` and `FDB_BINARY_DIR`; Windows target macros.

Control flow: CMake substitutes configured options into preprocessor definitions. `FDB_RELEASE` implies `FDB_CLEAN_BUILD`; sanitizer defines combine into `USE_SANITIZER`; `USE_VALGRIND` defines `VALGRIND`.

State/persistence: build-time generated configuration only.

Dependencies/integration: included by compiled sources to choose platform features and instrumentation. Values depend on top-level CMake cache and platform.

Risks: path macros embed build/source directories in binaries. Incorrect sanitizer or Windows target substitution can change ABI/platform behavior.

Test signals: generated `config.h` inspection and successful compilation under configured build variants.
