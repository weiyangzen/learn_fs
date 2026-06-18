# sources/storage-engines/wiredtiger/tools/checksum_bitflip/CMakeLists.txt

## Purpose
This CMake file declares the `checksum_bitflip` diagnostic executable for WiredTiger. It uses the project helper `create_test_executable` and lists `checksum_bitflip.c` as the only source.

## Important APIs and targets
The important build API is `create_test_executable(checksum_bitflip SOURCES checksum_bitflip.c)`. Build properties, include directories, and link libraries are inherited from the helper rather than spelled out locally.

## Control flow and behavior
There is no conditional build logic. If the containing directory is included by the parent CMake configuration, the executable target is created.

## State, dependencies, and integration
The file depends on the parent WiredTiger CMake infrastructure defining `create_test_executable`. The generated binary integrates with developer diagnostics for checksum mismatch investigation.

## Risks and test signals
Risks are limited to build-system integration: if helper semantics change, the tool may miss internal include paths or libraries needed for `test_util.h` and checksum helpers. Signals are successful target generation and compilation of `checksum_bitflip.c`.
