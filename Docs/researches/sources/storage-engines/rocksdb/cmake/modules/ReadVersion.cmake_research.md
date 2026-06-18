# sources/storage-engines/rocksdb/cmake/modules/ReadVersion.cmake

## Purpose
Extracts RocksDB's semantic version from the public `include/rocksdb/version.h` header during CMake configuration.

## Important APIs and Control Flow
`get_rocksdb_version(version_var)` reads the version header from `CMAKE_CURRENT_SOURCE_DIR`, loops over `MAJOR`, `MINOR`, and `PATCH`, matches `#define ROCKSDB_<component> ([0-9]+)`, and builds `<major>.<minor>.<patch>` into the caller's variable with `PARENT_SCOPE`.

## Dependencies, Risks, and Test Signals
It depends on the exact macro spelling in `version.h` and a source-root-relative configure context. It persists only a CMake variable. Risks include silently using empty `CMAKE_MATCH_1` if a regex does not match and source layout assumptions in embedded builds. Package-version generation and CMake configure tests are the validation points.
