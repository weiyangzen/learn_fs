# sources/storage-engines/foundationdb/cmake/GetFmt.cmake

## Purpose
Provides fmt dependency acquisition for the FoundationDB build.

## Important APIs, Types, and Functions
Runs `find_package(fmt 11.1.4 EXACT CONFIG)` and falls back to FetchContent from `fmtlib/fmt` tag `11.1.4`.

## Control Flow and Integration
Consumers include this file before linking `fmt` targets. If no installed exact config exists, the dependency is added from source.

## State and Persistence
Depends on installed fmt config or network access to GitHub.

## Dependencies
FetchContent source/build state persists under the build tree.

## Risks and Test Signals
Risks include unverified FetchContent git tag and exact-version rigidity. Test signal is `fmt` target availability and successful downstream link.
