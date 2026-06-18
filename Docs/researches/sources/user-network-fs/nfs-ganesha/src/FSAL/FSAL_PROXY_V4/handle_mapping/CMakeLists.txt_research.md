# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/CMakeLists.txt

## Purpose
Builds the optional handle-mapping static library and two standalone test executables for FSAL_PROXY_V4.

## Important APIs, Types, and Functions
Defines `handlemapping_STAT_SRCS`, creates static library `handlemapping`, and builds `test_handle_mapping_db` and `test_handle_mapping`.

## Control Flow
CMake compiles mapping sources, applies sanitizer instrumentation, adds LTTng generated-header dependencies when enabled, then links tests against `handlemapping`, `hashtable`, `log`, `common_utils`, `rwlock`, and `sqlite3`.

## State and Persistence Behavior
No runtime state. Build products enable the runtime SQLite-backed map and tests that mutate caller-supplied DB directories.

## Dependencies and Integration Points
Depends on SQLite and Ganesha utility libraries. Consumed by the higher FSAL_PROXY_V4 build when handle mapping is enabled.

## Risks
Tests are executables but not registered with CTest here. Test sources appear stale relative to current headers, so compile or link failures may expose API drift.

## Test Signals
Successful library/test builds and manual execution of the two test binaries with a scratch DB directory.
