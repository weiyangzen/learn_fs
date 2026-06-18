# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindToolchain.cmake

## Purpose

`FindToolchain.cmake` records basic host toolchain facts for conditional build behavior. It detects MSVC on Windows and GNU gold linker on Unix.

## Important APIs, Types, and Functions

The module sets `MSVC` when `CMAKE_SYSTEM_NAME` matches Windows and `CMAKE_CXX_COMPILER_ID` matches MSVC. It sets `GOLD_LINKER` when `ld -V` succeeds and reports `GNU gold`.

## Control Flow

On Windows it checks the C++ compiler ID. On Unix it runs `execute_process(COMMAND ld -V)`, captures result and output, and scans for `GNU gold`. It finishes with a status message.

## State and Persistence Behavior

State is limited to CMake variables in the configure process. The only external process is `ld -V`; no files are created.

## Dependencies and Integration Points

It depends on CMake system/compiler variables and an `ld` executable in PATH on Unix. Consumers can conditionally set linker flags or workarounds based on `GOLD_LINKER`.

## Risks and Edge Cases

Hardcoding `ld -V` may not reflect the actual linker used by the compiler driver, especially with Clang, lld, mold, cross-compilers, or `-fuse-ld`. The `MSVC` variable duplicates CMake's built-in `MSVC` semantics and may be redundant.

## Test Signals

Configure on GNU ld, gold, lld, and Windows/MSVC environments and inspect the resulting variables. Linker-specific flags should be tested through an actual target link.
