# sources/storage-engines/foundationdb/contrib/crc32/CMakeLists.txt

## Purpose
Builds the CRC32/CRC32C support library used by FoundationDB contrib code.

## Important APIs, Types, And Functions
Defines static library target `crc32` from `crc32.S`, `crc32_wrapper.c`, and `crc32c.cpp`. Disables clang-tidy for both C and C++ on the target. Adds a Clang-only `-Wno-unused-function` workaround. Publishes `include/` as a public include directory.

## Control Flow
CMake evaluates the target unconditionally, then conditionally applies the warning flag when `CLANG` is true.

## State And Persistence
No runtime state. It affects build graph state and include propagation.

## Dependencies And Integration
Integrates the mixed C/C++/assembly CRC implementation into the FoundationDB CMake build. Consumers include headers under `crc32/`.

## Risks
The static target always lists PowerPC assembly, relying on preprocessor guards inside `crc32.S` for non-PowerPC platforms. The warning suppression is broad across the target. Build behavior depends on project-level definition of `CLANG`.

## Test Signals
Configure and build on x86_64, aarch64, and ppc64 where available; verify public includes and that `crc32c_append` links from a consumer target.
