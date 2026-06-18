# sources/storage-engines/foundationdb/flow/ApiVersion.h.cmake

## Purpose
`ApiVersion.h.cmake` is a configured header template that generates `flow/ApiVersion.h`. It centralizes FoundationDB client API-version feature gates.

## Important APIs, Types, and Functions
The main type is `ApiVersion`, a constexpr wrapper around an integer version. It exposes `LATEST_VERSION`, `isValid`, `version`, comparison operators, and generated feature helpers. The `API_VERSION_FEATURE(v, x)` macro defines a feature marker struct, `hasX()` predicate, and `withX()` constructor for each feature.

## Control Flow
CMake substitutes placeholders such as `@FDB_AV_LATEST_VERSION@` and individual `@FDB_AV_*@` values from `ApiVersions.cmake`. Runtime code can then compare an `ApiVersion` against the feature's introduction version without string parsing or generated lookup tables.

## State and Persistence Behavior
There is no mutable or persistent state. The generated header embeds API-version constants into compiled code. `noBackwardsCompatibility` defines the lower valid bound.

## Dependencies and Integration Points
It includes `flow/Trace.h` and `<cstdint>`. `flow/CMakeLists.txt` configures this file into the build include directory. Client and binding code can use `hasFeature` methods to guard behavior by selected API version.

## Risks and Edge Cases
Feature constants must not exceed `LATEST_VERSION`; the macro enforces this with `static_assert`. Any missing semicolon in macro uses can affect generated C++ syntax; one feature line intentionally lacks a visible semicolon because the macro expands to declarations.

## Test Signals
Compile-time generation and compilation are the primary tests. Feature behavior is indirectly tested anywhere client API-version gates are exercised.
