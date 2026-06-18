# sources/storage-engines/foundationdb/contrib/CMakeLists.txt

## Purpose
Adds third-party and contrib libraries/tools used by FoundationDB.

## Important APIs, Types, and Functions
Creates `rapidjson` interface include target and adds subdirectories for crc32, stacktrace, folly_memcpy, rapidxml, sqlite, SimpleOpt, md5, libb64, plus non-Windows linenoise/debug_determinism/monitoring.

## Control Flow and Integration
Top-level FoundationDB CMake includes this directory to make bundled contrib dependencies available to main targets.

## State and Persistence
Depends on the listed contrib directories and platform variable `WIN32`.

## Dependencies
State is the CMake targets exported by each contrib subdirectory; no files generated here directly.

## Risks and Test Signals
Risks include missing subdirectories and platform-only tools not being built on Windows. Test signal is successful configuration of all contrib subdirectories.
