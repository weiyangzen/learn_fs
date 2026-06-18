# sources/storage-engines/foundationdb/contrib/libb64/CMakeLists.txt

## Purpose
This CMake file builds the vendored libb64 base64 helper library for FoundationDB.

## Important APIs, Types, And Functions
It declares `add_library(libb64 STATIC cdecode.c cencode.c)`, disables clang-tidy for the target with `C_CLANG_TIDY ""`, and publishes the local `include` directory with `target_include_directories(libb64 PUBLIC ...)`.

## Control Flow
CMake configures a static library target from the C encoder and decoder sources. Consumers linking to `libb64` inherit the public include path.

## State And Persistence Behavior
The file affects build graph state only. It creates no runtime persistence.

## Dependencies And Integration Points
It integrates with the parent FoundationDB CMake build and with headers under `include/libb64`. Disabling clang-tidy acknowledges vendored/public-domain C style that may not meet project lint rules.

## Risks And Edge Cases
Only C sources are compiled into the static library; C++ wrapper headers are header-only consumers. Build failures would likely come from include-path changes or parent target policy changes.

## Test Signals
Build-system tests should verify the `libb64` target compiles, exports headers, and links into any FDB components that include `libb64/cencode.h`, `libb64/cdecode.h`, or the C++ wrappers.
